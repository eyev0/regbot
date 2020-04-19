import shelve

from aiogram import types
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaDocument, InputFile
from aiogram.utils.exceptions import MessageNotModified

from bot import dp, bot, logging
from config import admin_ids, file, RANDOM_KITTEN_JPG
from keyboards import keyboard
from messages import msg_header_admin, msg_body_admin
from utils import UserDbAccessObject, User

db_access = UserDbAccessObject()


@dp.message_handler(lambda m: m.from_user.id in admin_ids,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    size = db_access.size()

    if size == 0:
        await message.reply(msg_header_admin(size) +
                            'Упс! Кажется, никто ещё не достучался до нас...',
                            parse_mode=ParseMode.MARKDOWN,
                            reply=False)
        return

    user = db_access.current()
    await message.reply(msg_header_admin(size) +
                        msg_body_admin(user),
                        parse_mode=ParseMode.MARKDOWN,
                        reply=False)
    if user.payment is not None:
        if user.payment.file_type == 'photo':
            await bot.send_photo(message.chat.id,
                                 photo=user.payment.file_id,
                                 reply_markup=keyboard)
        else:
            await bot.send_document(message.chat.id,
                                    document=user.payment.file_id,
                                    reply_markup=keyboard)
    else:
        await bot.send_document(message.chat.id,
                                document=InputFile.from_url(RANDOM_KITTEN_JPG,
                                                            'Ой! Ещё нет информации о платеже!'),
                                reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'back')
async def process_callback_button_prev(callback_query: types.CallbackQuery):
    await process_callback_button(callback_query, db_access.prev)


@dp.callback_query_handler(lambda c: c.data == 'forward')
async def process_callback_button_next(callback_query: types.CallbackQuery):
    await process_callback_button(callback_query, db_access.next)


def get_user_input_media_obj(user: User):
    if user.payment is not None:
        if user.payment.file_type == 'photo':
            media = InputMediaPhoto(user.payment.file_id)
        else:
            media = InputMediaDocument(user.payment.file_id)
    else:
        media = InputMediaDocument(InputFile.from_url(RANDOM_KITTEN_JPG,
                                                      'Ой! Ещё нет информации о платеже!'))
    return media


async def process_callback_button(callback_query: types.CallbackQuery,
                                  get_new_user_method):
    await bot.answer_callback_query(callback_query.id)

    size = db_access.size()
    user: User = get_new_user_method()
    assert user is not None
    media = get_user_input_media_obj(user)

    try:
        await bot.edit_message_text(msg_header_admin(size) +
                                    msg_body_admin(user),
                                    callback_query.message.chat.id,
                                    callback_query.message.message_id - 1,
                                    parse_mode=ParseMode.MARKDOWN)
    except MessageNotModified:
        logging.info(f'Message {callback_query.message.message_id - 1} is not modified')
    try:
        await callback_query.message.edit_media(media, reply_markup=keyboard)
    except MessageNotModified:
        logging.info(f'Message {callback_query.message.message_id} is not modified')


@dp.message_handler(lambda m: m.from_user.id in admin_ids,
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
