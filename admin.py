import shelve

from aiogram import types
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaDocument

from bot import dp, bot
from config import admin_id, file
from keyboards import keyboard
from messages import msg_header_admin
from utils import UserDbAccessObject

dbaccess = UserDbAccessObject()


@dp.message_handler(lambda m: m.from_user.id == admin_id,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    size = dbaccess.size()

    if size == 0:
        await message.reply(msg_header_admin(size) +
                            'Упс! Кажется, никто ещё не достучался до нас...',
                            parse_mode=ParseMode.MARKDOWN,
                            reply=False)
        return

    user = dbaccess.current()
    await message.reply(msg_header_admin(size) +
                        f'id: {user.user_id}\n'
                        f'username: @{user.username}\n'
                        f'Фамилия и имя: {user.name_surname}\n',
                        parse_mode=ParseMode.MARKDOWN,
                        reply=False)
    if user.payment.file_type == 'photo':
        await bot.send_photo(message.chat.id,
                             photo=user.payment.file_id,
                             reply_markup=keyboard)
    else:
        await bot.send_document(message.chat.id,
                                document=user.payment.file_id,
                                reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'back')
async def process_callback_button_prev(callback_query: types.CallbackQuery):
    await process_callback_button(callback_query, dbaccess.prev)


@dp.callback_query_handler(lambda c: c.data == 'forward')
async def process_callback_button_next(callback_query: types.CallbackQuery):
    await process_callback_button(callback_query, dbaccess.next)


async def process_callback_button(callback_query: types.CallbackQuery,
                                  get_new_user_method):
    size = dbaccess.size()
    curr_user = dbaccess.current()
    user = get_new_user_method()

    await bot.answer_callback_query(callback_query.id)

    if user is None:
        return

    if curr_user.user_id != user.user_id:
        await bot.edit_message_text(msg_header_admin(size) +
                                    f'id: {user.user_id}\n'
                                    f'username: @{user.username}\n'
                                    f'Фамилия и имя: {user.name_surname}\n',
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id - 1,
                                    parse_mode=ParseMode.MARKDOWN)

        if user.payment.file_type == 'photo':
            media = InputMediaPhoto(user.payment.file_id)
        else:
            media = InputMediaDocument(user.payment.file_id)
        await callback_query.message.edit_media(media, reply_markup=keyboard)


@dp.message_handler(lambda m: m.from_user.id == admin_id,
                    state='*',
                    commands=['delete'])
async def process_delete_command(message: types.Message):
    argument = message.get_args()

    with shelve.open(filename=file, writeback=True) as db:
        if db.get(argument) is not None:
            username = db[argument].username
            del db[argument]
            await message.reply(f'Запись юзера @{username} удалена',
                                reply=False)
