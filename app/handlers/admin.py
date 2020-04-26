import logging

from aiogram import types
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile
from aiogram.utils.exceptions import MessageNotModified, BadRequest

from app.bot import dp, bot
from app.config import Config
from app.const.keyboards import keyboard_scroll, keyboard_refresh
from app.db import session_scope
from app.db.models import User, Enrollment
from app.db.dao import UserDAO, EnrollmentDAO

kitty = InputFile.from_url(Config.RANDOM_KITTEN_JPG, 'Ой! Ещё нет информации о платеже!.jpg')
event_id = 1


def build_header_message(all_users_count: int,
                         new_users_count: int,
                         all_names: list):
    # build Header message
    m_h = 'Привет, admin! \n\n' \
          f'Регистраций: {str(all_users_count)} \n' \
          f'Новых: {str(new_users_count)}\n\n' \
          f'Список:\n' + \
          '_______________________\n' + \
          '\n'.join(all_names) + '\n'
    return m_h


def build_body_message(user: User):
    m_b = f'id: {user.uid}, ' + (f'@{user.username}\n' if user.username is not None else '\n') + \
          f'ФИО: {user.name_surname}\n' + \
          'Зареган: ' + ('да' if user.is_registered else 'нет') + '\n' \
                                                                  f'Когда: {user.edit_datetime}'
    return m_b


@dp.message_handler(lambda m: m.from_user.id in Config.admin_ids,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    with session_scope() as session:
        query = session.query(User, Enrollment)\
            .join(Enrollment)\
            .filter(Enrollment.event_id == event_id)

        # get all user data
        result = query.all()
        users_enrolled = [x[0] for x in result]
        new_enrolled = users_enrolled
        all_names = [x.name_surname for x in users_enrolled]
        # TODO: fetch..
        enrollment: Enrollment = EnrollmentDAO.fetch(session, direction=None)

        # header message
        m_h = build_header_message(len(users_enrolled),
                                   len(new_enrolled),
                                   all_names)
        # send header
        await message.reply(m_h,
                            reply=False,
                            reply_markup=keyboard_refresh)

        if enrollment is None:
            return

        # body message
        m_b = build_body_message(enrollment)
        # send body
        if enrollment.is_registered:
            try:
                if enrollment.file_type == 'photo':
                    await bot.send_photo(message.chat.id,
                                         photo=enrollment.file_id,
                                         caption=m_b,
                                         reply_markup=keyboard_scroll)
                else:
                    await bot.send_document(message.chat.id,
                                            document=enrollment.file_id,
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
        all_users_list = UserDAO.get_all_list(session)
        new_users_list = UserDAO.get_new_list(session)
        all_names = [x.name_surname for x in all_users_list]

        # header message
        m_h = build_header_message(len(all_users_list),
                                   len(new_users_list),
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
        next_user: User = UserDAO.fetch(session, direction=callback_query.data)
        try:
            await callback_query.message.edit_media(media(next_user), reply_markup=keyboard_scroll)
        except MessageNotModified:
            logging.info(f'Message {callback_query.message.message_id} is not modified')
        except BadRequest:
            # can't send media
            await callback_query.message.edit_media(InputMediaDocument(kitty, caption=build_body_message(next_user)),
                                                    reply_markup=keyboard_scroll)

        await bot.answer_callback_query(callback_query.id)


@dp.message_handler(lambda m: m.from_user.id in Config.admin_ids,
                    state='*',
                    commands=['delete'])
async def process_delete_command(message: types.Message):
    uid_to_delete = message.get_args()
    with session_scope() as session:
        user: User = UserDAO.get_by_uid(session, uid_to_delete)
        if user is not None:
            user.delete_me(session)
    await message.reply(f'Запись удалена!',
                        reply=False)


@dp.message_handler(lambda m: m.from_user.id in Config.admin_ids,
                    state='*',
                    commands=['reset_state'])
async def process_delete_command(message: types.Message):
    uid_to_reset = message.get_args()
    with session_scope() as session:
        user: User = UserDAO.get_by_uid(session, uid_to_reset)
        if user is not None:
            state = dp.current_state(user=uid_to_reset)
            await state.set_state(None)
            await message.reply(f'Состояние юзера {user.name_surname}, id={uid_to_reset} сброшено',
                                reply=False)
