from aiogram import types

from app import dp, bot
from app.db import session_scope
from app.db.models import User
from app.handlers import notifications_buttons_list, get_notifications_keyboard


@dp.callback_query_handler(lambda c: c.data in [x.callback_data for x in notifications_buttons_list],
                           state='*')
async def edit_notification_settings(callback_query: types.CallbackQuery):
    message = callback_query.message
    uid = callback_query.from_user.id
    with session_scope() as session:
        user_q = session.query(User) \
            .filter(User.uid == uid)
        user: User = user_q.all()[0]
        user.receive_notifications = not user.receive_notifications
        await message.edit_reply_markup(reply_markup=get_notifications_keyboard(user.receive_notifications))

    await bot.answer_callback_query(callback_query.id)
