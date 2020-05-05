import logging

from aiogram import types
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile, ReplyKeyboardRemove, ParseMode
from aiogram.utils.exceptions import MessageNotModified, BadRequest

from app import dp, bot
from app.config import Config
from app.const.messages import MESSAGES
from app.db import session_scope
from app.db.models import User, Enrollment, Event
from app.handlers.utils.keyboards import keyboard_scroll, keyboard_refresh, events_reply_keyboard
from app.handlers.utils.utils import WrappingListIterator, States, EventIdHolder, admin_lambda

kitty = InputFile.from_url(Config.RANDOM_KITTEN_JPG, 'Ой! Ещё нет информации о платеже!.jpg')


def build_header(all_users_count: int,
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


def build_caption(uid,
                  username,
                  name_surname,
                  complete,
                  edit_datetime):
    m_b = f'id: {uid}, ' + (f'@{username}\n' if username is not None else '\n') + \
          f'ФИО: {name_surname}\n' + \
          'Зареган: ' + ('да' if complete else 'нет') + '\n' + \
          f'Когда: {edit_datetime}'
    return m_b


@dp.message_handler(state='*',
                    commands=['admin'])
async def process_admin_command(message: types.Message):
    magic_word = message.get_args()
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    await state.set_state(None)
    if magic_word == 'pls':
        if uid not in Config.admin_ids:
            Config.admin_ids.append(uid)
            await message.reply(MESSAGES['admin_enable'], reply=False)
    elif magic_word == 'no':
        if uid in Config.admin_ids:
            Config.admin_ids.remove(uid)
            await message.reply(MESSAGES['admin_disable'], reply=False)


@dp.message_handler(state='*',
                    commands=['help'])
async def process_help_command(message: types.Message):
    m_text = MESSAGES['help_message']
    await message.reply(m_text, parse_mode=ParseMode.MARKDOWN, reply=False)


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['delete'])
async def process_delete_command(message: types.Message):
    uid_to_delete = message.get_args()
    with session_scope() as session:
        user_q = session.query(User) \
            .filter(User.uid == uid_to_delete)
        # get one record
        if user_q.count() > 0:
            user: User = user_q.all()[0]
            user.delete_me(session)
            await message.reply(f'Запись удалена!',
                                reply=False)


@dp.message_handler(state='*',
                    commands=['cancel'])
async def process_cancel_command(message: types.Message):
    await message.reply('Ok',
                        reply=False,
                        reply_markup=ReplyKeyboardRemove())


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['reset_state'])
async def process_reset_state_command(message: types.Message):
    uid_to_reset = message.get_args()
    with session_scope() as session:
        user_q = session.query(User) \
            .filter(User.uid == uid_to_reset)
        # get one record
        if user_q.count() > 0:
            user: User = user_q.all()[0]
            state = dp.current_state(user=uid_to_reset)
            await state.set_state(None)
            await message.reply(f'Состояние юзера {user.name_surname}, id={uid_to_reset} сброшено',
                                reply=False)


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    with session_scope() as session:
        events_q = session.query(Event) \
            .filter(Event.status < 9) \
            .order_by(Event.edit_datetime.desc())

        if events_q.count() > 0:
            events_keyboard = events_reply_keyboard(events_q.all())
            await state.set_state(States.all()[1])
        else:
            events_keyboard = None

        await message.reply(MESSAGES['admin_events'],
                            reply=False,
                            reply_markup=events_keyboard)


@dp.message_handler(admin_lambda(),
                    state='*')
async def process_event_click(message: types.Message):
    stub: types.Message = await message.reply('...',
                                              reply=False,
                                              reply_markup=ReplyKeyboardRemove())
    await stub.delete()

    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.title == message.text)
        if event_q.count() == 0:
            await message.reply('Нет такого..',
                                reply=False)
            return
        event: Event = event_q.all()[0]
        EventIdHolder.event_id = event.id

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == EventIdHolder.event_id) \
            .order_by(Enrollment.edit_datetime.desc())
        # get all user and enrollment data
        users_enrolls_list, count = users_enrolls_q.all(), users_enrolls_q.count()
        all_names = [x[0].name_surname for x in users_enrolls_list]

        # header message
        m_h = build_header(count,
                           count,
                           all_names)
        # send header
        await message.reply(m_h,
                            reply=False,
                            reply_markup=keyboard_refresh)

        if count == 0:
            return

        # get one record
        user, enrollment = WrappingListIterator.get_obj().fetch(users_enrolls_list)

        # body message
        m_b = build_caption(user.uid,
                            user.username,
                            user.name_surname,
                            enrollment.complete,
                            enrollment.edit_datetime)
        # send body
        if enrollment.complete:
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


# get media


@dp.callback_query_handler(lambda c: c.data in ['refresh'],
                           state='*')
async def process_callback_button_refresh_header(callback_query: types.CallbackQuery):
    with session_scope() as session:
        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == EventIdHolder.event_id) \
            .order_by(Enrollment.edit_datetime.desc())
        # get all user and enrollment data
        users_enrolls_list, count = users_enrolls_q.all(), users_enrolls_q.count()
        all_names = [x[0].name_surname for x in users_enrolls_list]

        # header message
        m_h = build_header(count,
                           count,
                           all_names)

        # edit header
        try:
            await callback_query.message.edit_text(m_h, reply_markup=keyboard_refresh)
        except MessageNotModified:
            logging.info(f'Message {callback_query.message.message_id} is not modified')

    await bot.answer_callback_query(callback_query.id)


def media_with_caption(enroll_complete, file_type, file_id, caption):
    if enroll_complete:
        if file_type == 'photo':
            obj = InputMediaPhoto(file_id, caption=caption)
        else:
            obj = InputMediaDocument(file_id, caption=caption)
    else:
        obj = InputMediaDocument(kitty, caption=caption)
    return obj


@dp.callback_query_handler(lambda c: c.data in ['back', 'forward', 'rewind_back', 'rewind_forward'],
                           state='*')
async def process_callback_button_scroll(callback_query: types.CallbackQuery):
    with session_scope() as session:
        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == EventIdHolder.event_id) \
            .order_by(Enrollment.edit_datetime.desc())
        # get all user and enrollment data
        users_enrolls_list = users_enrolls_q.all()
        # get one record
        user, enrollment = WrappingListIterator.get_obj().fetch(users_enrolls_list,
                                                                direction=callback_query.data)

        caption = build_caption(user.uid,
                                user.username,
                                user.name_surname,
                                enrollment.complete,
                                enrollment.edit_datetime)
        try:
            await callback_query.message.edit_media(media_with_caption(enrollment.complete,
                                                                       enrollment.file_type,
                                                                       enrollment.file_id,
                                                                       caption),
                                                    reply_markup=keyboard_scroll)
        except MessageNotModified:
            logging.info(f'Message {callback_query.message.message_id} is not modified')
        except BadRequest:
            # can't send media
            await callback_query.message.edit_media(
                InputMediaDocument(kitty, caption=caption),
                reply_markup=keyboard_scroll)

        await bot.answer_callback_query(callback_query.id)
