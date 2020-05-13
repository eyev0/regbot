from aiogram import types
from aiogram.utils.exceptions import BadRequest

from app import dp, bot
from app.db import session_scope
from app.db.models import Enrollment, User, Event
from app.db.util import WrappingListIterator
from app.handlers import MenuStates, CreateEventStates, ChangeStatusStates, PublishStates
from app.handlers.admin import kitty, process_start_command_admin, show_events_task_admin
from app.handlers.keyboards import keyboard_refresh, keyboard_scroll, button_create_new, \
    keyboard_admin_menu, button_view_enrolls, button_change_status, button_publish, button_back_to_events, \
    button_cancel, keyboard_cancel, button_view_archive, keyboard_change_status, button_back_to_event_menu
from app.handlers.messages import build_header, build_caption, MESSAGES


@dp.message_handler(lambda m: m.text == button_create_new.text,
                    state=MenuStates.MENU_STATE_0)
@dp.message_handler(state=CreateEventStates.all())
async def process_create_event_data(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    state_number = int(str(await state.get_state())[-1:])
    state_data = await state.get_data() or {}
    if state_number > 0:
        input_data = message.text if message.text != '-' else ''
        if input_data == button_cancel.text:
            await state.set_state(MenuStates.all()[0])
            await state.set_data({})
            await process_start_command_admin(message)
            return
        state_data[state_number] = input_data
        await state.set_data(state_data)

    if state_number < 3:
        state_number += 1
        await state.set_state(CreateEventStates.all()[state_number])
        await message.reply(MESSAGES['create_event_prompt_data_' + str(state_number)],
                            reply=False,
                            reply_markup=keyboard_cancel)
    else:
        with session_scope() as session:
            Event(title=state_data[1],
                  description=state_data[2],
                  access_info=state_data[3]) \
                .insert_me(session)
        await message.reply(MESSAGES['create_event_done'],
                            reply=False)
        await state.set_state(MenuStates.all()[0])
        await state.set_data({})
        await process_start_command_admin(message)


@dp.message_handler(lambda m: m.text == button_view_archive.text,
                    state=MenuStates.MENU_STATE_0)
async def process_view_archive_admin(message: types.Message):
    await show_events_task_admin(message, archived=True)


@dp.message_handler(lambda m: m.text == button_back_to_event_menu.text,
                    state=ChangeStatusStates.CHANGE_STATUS_STATE_0 | PublishStates.PUBLISH_STATE_0)
@dp.message_handler(state=MenuStates.MENU_STATE_0)
async def process_event_click_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    event_title = message.text
    with session_scope() as session:
        event_q = session.query(Event)
        if event_title == button_back_to_event_menu.text:
            state_data = await state.get_data()
            event_q = event_q.filter(Event.id == state_data['event_id'])
        else:
            event_q = event_q.filter(Event.title == event_title)
        if event_q.count() == 0:
            await message.reply(MESSAGES['admin_event_not_found'],
                                reply=False)
            return
        event: Event = event_q.all()[0]
        data = {'event_id': event.id}
        await state.set_state(MenuStates.all()[1])
        await state.set_data(data)
        await message.reply(MESSAGES['admin_event_submenu'],
                            reply=False,
                            reply_markup=keyboard_admin_menu)


@dp.message_handler(lambda m: m.text == button_view_enrolls.text,
                    state=MenuStates.MENU_STATE_1_EVENT)
async def process_view_enrolls_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    state_data = await state.get_data()
    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.id == state_data['event_id'])
        if event_q.count() == 0:
            await message.reply(MESSAGES['admin_event_not_found'],
                                reply=False)
            return

        event: Event = event_q.all()[0]
        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == state_data['event_id']) \
            .order_by(Enrollment.edit_datetime.desc())
        # get all user and enrollment data
        users_enrolls_list, count = users_enrolls_q.all(), users_enrolls_q.count()
        all_names = [x[0].name_surname for x in users_enrolls_list]

        # header message
        m_h = build_header(event.title,
                           event.id,
                           count,
                           all_names)
        # send header
        await message.reply(m_h,
                            reply=False,
                            reply_markup=keyboard_refresh)

        if count == 0:
            return

        # get one record
        user, enrollment = WrappingListIterator.get_obj().fetch(users_enrolls_list)

        # body message
        m_b = build_caption(user.uid,
                            user.username,
                            user.name_surname,
                            enrollment.complete,
                            enrollment.edit_datetime)
        # send body
        if enrollment.complete:
            try:
                if enrollment.file_type == 'photo':
                    await bot.send_photo(message.chat.id,
                                         photo=enrollment.file_id,
                                         caption=m_b,
                                         reply_markup=keyboard_scroll)
                else:
                    await bot.send_document(message.chat.id,
                                            document=enrollment.file_id,
                                            caption=m_b,
                                            reply_markup=keyboard_scroll)
            except BadRequest:
                # can't send media
                await bot.send_document(message.chat.id,
                                        document=kitty,
                                        caption=m_b,
                                        reply_markup=keyboard_scroll)
        else:
            await bot.send_document(message.chat.id,
                                    document=kitty,
                                    caption=m_b,
                                    reply_markup=keyboard_scroll)


@dp.message_handler(lambda m: m.text == button_change_status.text,
                    state=MenuStates.MENU_STATE_1_EVENT)
async def process_change_status_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    await state.set_state(ChangeStatusStates.all()[0])
    await message.reply(MESSAGES['change_status_prompt'],
                        reply=False,
                        reply_markup=keyboard_change_status)


@dp.message_handler(lambda m: m.text == button_publish.text,
                    state=MenuStates.MENU_STATE_1_EVENT)
async def process_publish_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    with session_scope() as session:
        pass


@dp.message_handler(lambda m: m.text == button_back_to_events.text,
                    state=MenuStates.MENU_STATE_1_EVENT)
async def process_back_to_events_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    await state.set_state(MenuStates.all()[0])
    await show_events_task_admin(message)
