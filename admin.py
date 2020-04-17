import shelve

from aiogram import types
from aiogram.types import ParseMode

from bot import dp, bot
from config import admin_id, file
from keyboards import keyboard


@dp.message_handler(lambda m: m.from_user.id == admin_id, state='*', commands=['start'])
async def process_start_command(message: types.Message):
    with shelve.open(filename=file, writeback=True) as db:
        # дзынь тут
        ids = db.keys()
        if len(ids) > 0:
            current_user = db[ids[0]]

    await message.reply('Привет, admin! '
                        'Смотри, сколько людей зарегалось!\n\n'
                        '*Регистраций*: ' + str(len(ids)) + '\n\n'
                        'username: @' + current_user['username'] + '\n'
                        'Фамилия и имя: ' + current_user['name_surname'] + '\n'
                        # и вот тут
                        ,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboard,
                        reply=False)


@dp.callback_query_handler(lambda c: c.data == '<')
async def process_callback_button_prev(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')


@dp.callback_query_handler(lambda c: c.data == '>')
async def process_callback_button_next(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')
