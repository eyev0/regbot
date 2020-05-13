from aiogram import types

from app import dp, bot
from app.db import session_scope, enrolls_row_iterator
from app.db.models import Event, User, Enrollment
from app.handlers import MenuStates, ChangeStatusStates
from app.handlers.admin import send_enrollment_message, send_user_list_message, send_event_message
from app.handlers.keyboards import button_refresh, scroll_buttons_list, \
    button_view_enrolls, status_buttons_list, button_publish, button_current_status
from app.handlers.messages import MESSAGES


# view enrolls click
@dp.callback_query_handler(lambda c: c.data == button_view_enrolls.callback_data,
                           state=MenuStates.MENU_STATE_1_EVENT)
# refresh click
@dp.callback_query_handler(lambda c: c.data == button_refresh.callback_data,
                           state=MenuStates.MENU_STATE_1_EVENT)
# scroll click
@dp.callback_query_handler(lambda c: c.data in [x.callback_data for x in scroll_buttons_list],
                           state=MenuStates.MENU_STATE_1_EVENT)
async def view_enrolls(callback_query: types.CallbackQuery):
    refresh_header = scroll = view = edit = False
    if callback_query.data == button_refresh.callback_data:
        refresh_header = edit = True
    elif callback_query.data in [x.callback_data for x in scroll_buttons_list]:
        scroll = edit = True
    else:
        view = True

    uid = callback_query.from_user.id
    message = callback_query.message
    state = dp.current_state(user=uid)
    state_data = await state.get_data()
    with session_scope() as session:
        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == state_data['event_id']) \
            .order_by(Enrollment.edit_datetime.desc())

        user_enroll_list, enrolled_count = users_enrolls_q.all(), users_enrolls_q.count()
        names_list = [x[0].name_surname for x in user_enroll_list]

        if (refresh_header or view) and enrolled_count > 0:
            await send_user_list_message(message, names_list, edit=edit)

        if (view and enrolled_count > 0) or scroll:
            user, enrollment = enrolls_row_iterator.fetch(user_enroll_list,
                                                          do_scroll=scroll,
                                                          where=callback_query.data)
            await send_enrollment_message(message, user, enrollment, edit=edit)

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data == [x.callback_data for x in status_buttons_list],
                           state=MenuStates.MENU_STATE_1_EVENT)
async def change_status(callback_query: types.CallbackQuery):
    refresh = scroll = False
    if callback_query.data == button_current_status:
        refresh = True
    else:
        scroll = True

    uid = callback_query.from_user.id
    message = callback_query.message
    state = dp.current_state(user=uid)
    state_data = await state.get_data()
    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.id == state_data['event_id'])

        event: Event = event_q.all()[0]
        status = event.status

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == state_data['event_id']) \
            .order_by(Enrollment.edit_datetime.desc())
        count = users_enrolls_q.count()

        if scroll:
            Event.status_map[event.status]
        await send_event_message(message, event, count, edit=True)

    await state.set_state(ChangeStatusStates.all()[0])
    pass


@dp.callback_query_handler(lambda c: c.data == button_publish.callback_data,
                           state=MenuStates.MENU_STATE_1_EVENT)
async def publish(callback_query: types.CallbackQuery):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    with session_scope() as session:
        pass


@dp.callback_query_handler(state='*')
async def restart_prompt(callback_query: types.CallbackQuery):
    await callback_query.message.reply(MESSAGES['admin_restart'],
                                       reply=False)
    await bot.answer_callback_query(callback_query.id)
    return
