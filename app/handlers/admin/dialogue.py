from aiogram import types
from aiogram.types import ContentTypes

from app import dp, admin_nav_context
from app.db import session_scope
from app.db.models import Event, User, Enrollment
from app.handlers.util.states import MenuStates, CreateEventStates, PublishStates
from app.handlers.admin import process_start_command_admin, show_events_task_admin, send_event_message
from app.handlers.util.keyboards import button_create_new, button_cancel, keyboard_cancel, button_view_archive, \
    keyboard_publish
from app.handlers.messages import MESSAGES, full_names_list_str


@dp.message_handler(lambda m: m.text == button_create_new.text,
                    state=MenuStates.MENU_STATE_0)
@dp.message_handler(state=CreateEventStates.all())
async def process_create_event_data(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    state_str = str(await state.get_state())
    state_number = int(state_str[-1:])
    state_data = await state.get_data() or {}
    if state_str in CreateEventStates.all():
        input_data = message.text if message.text != '-' else ''
        if input_data == button_cancel.text:
            await state.set_state(MenuStates.all()[0])
            await state.set_data({})
            await process_start_command_admin(message)
            return
        state_data[str(state_number)] = input_data
        await state.set_data(state_data)

    if state_number < len(CreateEventStates.all()) - 1:
        state_number += 1
        await state.set_state(CreateEventStates.all()[state_number])
        await message.reply(MESSAGES['create_event_prompt_data_' + str(state_number)],
                            reply=False,
                            reply_markup=keyboard_cancel)
    else:
        with session_scope() as session:
            Event(title=state_data['1'],
                  description=state_data['2'],
                  access_info=state_data['3']) \
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


@dp.message_handler(state=MenuStates.MENU_STATE_0)
async def process_event_click_admin(message: types.Message):
    uid = message.from_user.id
    event_title = message.text
    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.title == event_title)
        if event_q.count() == 0:
            await message.reply(MESSAGES['admin_event_not_found'],
                                reply=False)
            return
        event: Event = event_q.all()[0]

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == event.id) \
            .order_by(Enrollment.edit_datetime.desc())
        count = users_enrolls_q.count()

        result = await send_event_message(message, event, count)
        await admin_nav_context.save(user=uid, key=result.message_id, value=(event.id, 0,))


@dp.message_handler(state=PublishStates.PUBLISH_STATE_0,
                    content_types=ContentTypes.TEXT)
async def process_publish_message(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    state_data = await state.get_data()
    if message.text.lower() == 'отмена':
        await state.set_state(MenuStates.all()[0])
        return
    else:
        await state.set_state(PublishStates.all()[1])

    with session_scope() as session:
        users_q = session.query(User) \
            .filter(User.active == True) \
            .filter(User.receive_notifications == True)

        names_list = [x.full_name for x in users_q.all()]

    await message.reply(MESSAGES['admin_publish_user_list'] + full_names_list_str(names_list),
                        reply=False)
    result = await message.reply(message.text,
                                 reply=False,
                                 reply_markup=keyboard_publish)
    await admin_nav_context.save(user=uid,
                                 key='event_id_message_' + str(result.message_id),
                                 value=state_data['event_id'])
