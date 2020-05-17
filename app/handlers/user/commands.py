import logging

from aiogram import types
from aiogram.types import ParseMode, ReplyKeyboardRemove

from app import dp
from app.db import session_scope
from app.db.models import User
from app.handlers.states import UserStates
from app.handlers.messages import MESSAGES
from app.handlers.user.util import show_event_list_task
from app.handlers.lambdas import not_admin_lambda


@dp.message_handler(not_admin_lambda(),
                    state='*',
                    commands=['help'])
async def process_help_command(message: types.Message):
    m_text = MESSAGES['help_message']
    await message.reply(m_text, parse_mode=ParseMode.MARKDOWN, reply=False)


@dp.message_handler(not_admin_lambda(),
                    state='*',
                    commands=['cancel'])
async def process_cancel_command(message: types.Message):
    await message.reply('Ok',
                        reply=False,
                        reply_markup=ReplyKeyboardRemove())


@dp.message_handler(not_admin_lambda(),
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    with session_scope() as session:
        user_q = session.query(User) \
            .filter(User.uid == uid)

        if user_q.count() == 0:
            user = User(uid=uid,
                        username=message.from_user.username) \
                .insert_me(session)
            logging.info(f'user created: {user}')
            await state.set_state(UserStates.all()[1])  # greet and prompt for name and surname
            await message.reply(MESSAGES['greet_new_user'],
                                parse_mode=ParseMode.MARKDOWN,
                                reply=False)
        else:
            await show_event_list_task(message.from_user.id)
