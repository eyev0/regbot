import logging

from aiogram import types
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile
from aiogram.utils.exceptions import MessageNotModified, BadRequest

from regbot.bot import dp, bot
from regbot.config import Config
from regbot.const.keyboards import keyboard_scroll, keyboard_refresh
from regbot.db import session_scope, User
from regbot.utils import UserListIterator

kitty = InputFile.from_url(Config.RANDOM_KITTEN_JPG, 'Ой! Ещё нет информации о платеже!.jpg')


def build_header_message(all_users_count,
                         new_users_count,
                         all_names):
    # build Header message
    m_h = 'Привет, admin! \n\n' \
          f'Регистраций: {str(all_users_count)} \n' \
          f'Новых: {str(new_users_count)}\n\n' \
          f'Список:\n' + \
          '_______________________\n' + \
          '\n'.join(all_names) + '\n'
    return m_h


def build_body_message(user: User):
    m_b = f'id: {user.user_id}, ' + (f'@{user.username}\n' if user.username is not None else '\n') + \
          f'ФИО: {user.name_surname}\n' + \
          'Зареган: ' + ('да' if user.is_registered else 'нет') + '\n' \
                                                                  f'Когда: {user.edit_datetime}'
    return m_b


@dp.message_handler(lambda m: m.from_user.id in Config.admin_ids,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    with session_scope() as session:
        # get all user data
        all_users_q = session.query(User) \
            .order_by(User.edit_datetime.desc())
        new_users_q = all_users_q \
            .filter_by(admin_check=False)
        all_names = [x.name_surname for x in all_users_q.all()]
        it = UserListIterator.get_obj(admin_id=message.from_user.id)
        current_user: User = it.fetch(None, all_users_q.all())

        # header message
        m_h = build_header_message(all_users_q.count(),
                                   new_users_q.count(),
                                   all_names)

        # body message
        m_b = build_body_message(current_user)

        # send header
        await message.reply(m_h,
                            reply=False,
                            reply_markup=keyboard_refresh)
        # send body
        if current_user.is_registered:
            try:
                if current_user.file_type == 'photo':
                    await bot.send_photo(message.chat.id,
                                         photo=current_user.file_id,
                                         caption=m_b,
                                         reply_markup=keyboard_scroll)
                else:
                    await bot.send_document(message.chat.id,
                                            document=current_user.file_id,
                                            caption=m_b,
                                            reply_markup=keyboard_scroll)
            except BadRequest:
                # can't send media
                await bot.send_document(message.chat.id,
                                        document=kitty,
                                        caption=m_b,
                                        reply_markup=keyboard_scroll)
        else:
            await bot.send_document(message.chat.id,
                                    document=kitty,
                                    caption=m_b,
                                    reply_markup=keyboard_scroll)


@dp.callback_query_handler(lambda c: c.data in ['refresh'])
async def process_callback_button_refresh_header(callback_query: types.CallbackQuery):
    with session_scope() as session:
        # get all user data
        all_users_q = session.query(User) \
            .order_by(User.edit_datetime.desc())
        new_users_q = all_users_q \
            .filter_by(admin_check=False)
        all_names = [x.name_surname for x in all_users_q.all()]

        # header message
        m_h = build_header_message(all_users_q.count(),
                                   new_users_q.count(),
                                   all_names)

        # edit header
        try:
            await callback_query.message.edit_text(m_h, reply_markup=keyboard_refresh)
        except MessageNotModified:
            logging.info(f'Message {callback_query.message.message_id} is not modified')

    await bot.answer_callback_query(callback_query.id)


# get media
def media(user: User):
    if user.is_registered:
        if user.file_type == 'photo':
            obj = InputMediaPhoto(user.file_id, caption=build_body_message(user))
        else:
            obj = InputMediaDocument(user.file_id, caption=build_body_message(user))
    else:
        obj = InputMediaDocument(kitty, caption=build_body_message(user))
    return obj


@dp.callback_query_handler(lambda c: c.data in ['back', 'forward', 'rewind_back', 'rewind_forward'])
async def process_callback_button_scroll(callback_query: types.CallbackQuery):
    with session_scope() as session:
        # get all user data
        all_users_q = session.query(User) \
            .order_by(User.edit_datetime.desc())
        it = UserListIterator.get_obj(callback_query.message.from_user.id)
        current_user: User = it.fetch(callback_query.data, all_users_q.all())

        try:
            await callback_query.message.edit_media(media(current_user), reply_markup=keyboard_scroll)
        except MessageNotModified:
            logging.info(f'Message {callback_query.message.message_id} is not modified')
        except BadRequest:
            # can't send media
            await callback_query.message.edit_media(InputMediaDocument(kitty, caption=build_body_message(current_user)),
                                                    reply_markup=keyboard_scroll)

        await bot.answer_callback_query(callback_query.id)


@dp.message_handler(lambda m: m.from_user.id in Config.admin_ids,
                    state='*',
                    commands=['delete'])
async def process_delete_command(message: types.Message):
    u_id = message.get_args()

    with session_scope() as session:
        user = session.query(User) \
            .filter_by(user_id=u_id) \
            .all()
        if user is not None:
            session.delete(user[0])
            await message.reply(f'Запись юзера {user[0].name_surname}, id={user[0].id} удалена',
                                reply=False)
