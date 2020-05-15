from aiogram import types

from app import dp, navigation_context
from app.db import session_scope
from app.db.models import Event, User, Enrollment
from app.handlers import MenuStates, CreateEventStates
from app.handlers.admin import process_start_command_admin, show_events_task_admin, send_event_message
from app.handlers.keyboards import button_create_new, button_cancel, keyboard_cancel, button_view_archive
from app.handlers.messages import MESSAGES


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
        state_data[state_number] = input_data
        await state.set_data(state_data)

    if state_number < len(CreateEventStates.all()):
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
                    state=MenuStates.MENU_STATE_0 | MenuStates.MENU_STATE_1_EVENT)
async def process_view_archive_admin(message: types.Message):
    await show_events_task_admin(message, archived=True)


@dp.message_handler(state=MenuStates.MENU_STATE_0 | MenuStates.MENU_STATE_1_EVENT)
async def process_event_click_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
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
        await navigation_context.save(user=uid, key=result.message_id, value=(event.id, 0,))
        await state.set_state(MenuStates.all()[1])
