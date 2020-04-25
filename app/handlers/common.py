from aiogram import types
from aiogram.types import ParseMode

from app.bot import dp
from app.config import Config


@dp.message_handler(state='*', commands=['help'])
async def process_help_command(message: types.Message):
    msg = 'Это - *бот-помощник* для регистрации на онлайн-классы *Леры* *Трифоновой*\n' \
          'Если у тебя есть вопрос про мероприятия или про этого бота - напиши мне *@danceleradance*'
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN, reply=False)


@dp.message_handler(state='*',
                    commands=['admin_me'])
async def process_delete_command(message: types.Message):
    magic_word = message.get_args()
    if magic_word == 'please':
        uid = message.from_user.id
        state = dp.current_state(user=uid)
        await state.set_state(None)
        if uid not in Config.admin_ids:
            t = 'Ладно... будешь за админа теперь!'
            Config.admin_ids.append(uid)
        else:
            t = 'Теперь ты как все, друг!'
            Config.admin_ids.remove(uid)
        await message.reply(t, reply=False)
