import logging

from aiogram import types

from app import dp, bot, admin_nav_context, user_notify_context
from app.db import session_scope, fetch_list
from app.db.models import Event, User, Enrollment
from app.handlers.admin import send_enrollment_message, send_user_list_message, send_event_message, admin_lambda
from app.handlers.keyboards import button_refresh, scroll_buttons_list, \
    button_view_enrolls, status_buttons_list, button_publish, button_current_status, publish_buttons_list, \
    button_publish_edit, get_notifications_keyboard
from app.handlers.messages import MESSAGES
# view enrolls click
from app.handlers.states import PublishStates, MenuStates


@dp.callback_query_handler(lambda c: c.data == button_view_enrolls.callback_data,
                           state='*')
# refresh click
@dp.callback_query_handler(lambda c: c.data == button_refresh.callback_data,
                           state='*')
# scroll click
@dp.callback_query_handler(lambda c: c.data in [x.callback_data for x in scroll_buttons_list],
                           state='*')
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
    event_id, pos = await admin_nav_context.get(user=uid, key=message.message_id)
    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.id == event_id)

        event: Event = event_q.all()[0]

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == event_id) \
            .order_by(Enrollment.edit_datetime.desc())

        user_enroll_list, enrolled_count = users_enrolls_q.all(), users_enrolls_q.count()
        names_list = [x[0].full_name for x in user_enroll_list]

        if (view and enrolled_count > 0) or refresh_header:
            result = await send_user_list_message(message, event, names_list, edit=edit)
            await admin_nav_context.save(user=uid, key=result.message_id, value=(event.id, pos,))

        if (view and enrolled_count > 0) or scroll:
            (user, enrollment), pos = fetch_list(user_enroll_list,
                                                 current_pos=pos,
                                                 do_scroll=scroll,
                                                 where=callback_query.data)
            result = await send_enrollment_message(message, user, enrollment, edit=edit)
            await admin_nav_context.save(user=uid, key=result.message_id, value=(event.id, pos,))

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data in [x.callback_data for x in status_buttons_list],
                           state='*')
async def change_status(callback_query: types.CallbackQuery):
    scroll = callback_query.data != button_current_status.callback_data
    uid = callback_query.from_user.id
    message = callback_query.message
    event_id, _ = await admin_nav_context.get(user=uid, key=message.message_id)
    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.id == event_id)

        event: Event = event_q.all()[0]

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == event_id) \
            .order_by(Enrollment.edit_datetime.desc())
        count = users_enrolls_q.count()

        if scroll:
            list_ = [x for x in Event.status_map.keys()]
            pos = list_.index(event.status)
            new_status, pos = fetch_list(list_,
                                         current_pos=pos,
                                         do_scroll=scroll,
                                         where=callback_query.data)
            event.status = new_status
        await send_event_message(message, event, count, edit=True)

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data == button_publish.callback_data,
                           state='*')
async def publish(callback_query: types.CallbackQuery):
    message = callback_query.message
    uid = callback_query.from_user.id
    state = dp.current_state(user=uid)

    # store event_id of this message
    event_id, _ = await admin_nav_context.get(user=uid, key=message.message_id)
    await state.set_data({'event_id': event_id})

    await state.set_state(PublishStates.all()[0])
    await message.reply(MESSAGES['admin_publish_message'],
                        reply=False)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data in [x.callback_data for x in publish_buttons_list],
                           state=PublishStates.PUBLISH_STATE_1)
async def publish_edit_submit(callback_query: types.CallbackQuery):
    message = callback_query.message
    uid = callback_query.from_user.id
    state = dp.current_state(user=uid)
    event_id = await admin_nav_context.get(user=uid, key='event_id_message_' + str(message.message_id))
    if callback_query.data == button_publish_edit.callback_data:
        await state.set_state(PublishStates.all()[0])
        await message.reply(MESSAGES['admin_publish_edit'],
                            reply=False)
        await bot.answer_callback_query(callback_query.id)
        return
    with session_scope() as session:
        users_q = session.query(User) \
            .filter(User.active == True) \
            .filter(User.receive_notifications == True)

        result_map = {}
        for user in users_q.all():
            try:
                result = await bot.send_message(user.uid,
                                                message.text,
                                                reply_markup=get_notifications_keyboard(
                                                    flag=user.receive_notifications))
                await user_notify_context.save(user=user.uid, key=result.message_id, value=event_id)
                result_map[user.full_name] = True
            except Exception as e:
                logging.error('Exception sending notification to user:' + str(user) + ', exception is:\n\n' + str(e))
                result_map[user.full_name] = False

        result_str = 'Уведомление отправлено:\n'
        user_ls = [usr for usr in result_map.keys()]
        result_str = result_str + '\n'.join([name + (' - да' if result_map[name] else ' - нет') for name in user_ls])
        await message.reply(result_str,
                            reply=False)

    await message.edit_reply_markup(reply_markup=None)
    await state.set_state(MenuStates.all()[0])
    await bot.answer_callback_query(callback_query.id)

# @dp.callback_query_handler(admin_lambda(),
#                            state='*')
# async def restart_prompt(callback_query: types.CallbackQuery):
#     await callback_query.message.reply(MESSAGES['admin_restart'],
#                                        reply=False)
#     await bot.answer_callback_query(callback_query.id)
#     return
