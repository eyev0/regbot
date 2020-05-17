from aiogram import types

from app import dp, bot
from app.db import session_scope
from app.db.models import User
from app.handlers import toggle_notifications_buttons_list, get_notifications_keyboard, button_turn_notifications_on, \
    button_show_all_events
from app.handlers.user import show_event_list_task


@dp.callback_query_handler(lambda c: c.data in [x.callback_data for x in toggle_notifications_buttons_list],
                           state='*')
async def toggle_notification_click(callback_query: types.CallbackQuery):
    message = callback_query.message
    uid = callback_query.from_user.id
    with session_scope() as session:
        user_q = session.query(User) \
            .filter(User.uid == uid)
        user: User = user_q.all()[0]
        user.receive_notifications = (callback_query.data == button_turn_notifications_on.callback_data)
        await message.edit_reply_markup(reply_markup=get_notifications_keyboard(user.receive_notifications))

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data in [button_show_all_events.callback_data],
                           state='*')
async def show_all_events_click(callback_query: types.CallbackQuery):
    await show_event_list_task(callback_query.from_user.id)
    await bot.answer_callback_query(callback_query.id)
