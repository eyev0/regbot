import logging

from aiogram import types
from aiogram.types import InputFile, ParseMode, ReplyKeyboardRemove, InputMediaPhoto, InputMediaDocument, ContentType
from aiogram.utils.emoji import emojize
from aiogram.utils.exceptions import BadRequest, MessageNotModified
from aiogram.utils.markdown import text
from sqlalchemy import and_, or_

from app import Config, dp, bot, clock
from app.const.messages import MESSAGES, build_header, build_caption
from app.db import session_scope
from app.db.models import User, Event, Enrollment
from app.utils.keyboards import events_reply_keyboard, keyboard_refresh, keyboard_scroll
from app.utils.utils import admin_lambda, States, EventIdHolder, WrappingListIterator, not_admin_lambda

kitty = InputFile.from_url(Config.RANDOM_KITTEN_JPG, 'Ой! Ещё нет информации о платеже!.jpg')


@dp.message_handler(state='*',
                    commands=['admin'])
async def process_admin_command(message: types.Message):
    magic_word = message.get_args()
    uid = message.from_user.id
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


@dp.message_handler(state='*',
                    commands=['cancel'])
async def process_cancel_command(message: types.Message):
    await message.reply('Ok',
                        reply=False,
                        reply_markup=ReplyKeyboardRemove())


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['delete'])
async def process_delete_command(message: types.Message):
    args = message.get_args().split(' ')
    if len(args) < 2:
        return
    event_id = args[0]
    uid_to_delete = args[1]
    with session_scope() as session:
        enroll_q = session.query(Enrollment) \
            .join(User) \
            .filter(User.uid == uid_to_delete) \
            .filter(Enrollment.event_id == event_id)
        # get one record
        if enroll_q.count() > 0:
            enroll: Enrollment = enroll_q.all()[0]
            enroll.delete_me(session)
            await message.reply(f'Запись удалена!',
                                reply=False)


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['start'])
async def process_start_command_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    with session_scope() as session:
        events_q = session.query(Event) \
            .filter(Event.status < 9) \
            .order_by(Event.edit_datetime.desc())

        events_keyboard = events_reply_keyboard(events_q.all())

        await message.reply(MESSAGES['admin_events'],
                            reply=False,
                            reply_markup=events_keyboard)


@dp.message_handler(admin_lambda(),
                    state='*')
async def process_event_click_admin(message: types.Message):
    remove_keyboard_stub: types.Message = await message.reply('...',
                                                              reply=False,
                                                              reply_markup=ReplyKeyboardRemove())
    await remove_keyboard_stub.delete()

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
        m_h = build_header(event.title,
                           event.id,
                           count,
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


@dp.callback_query_handler(admin_lambda(),
                           lambda c: c.data in ['refresh'],
                           state='*')
async def process_callback_button_refresh_header(callback_query: types.CallbackQuery):
    if EventIdHolder.event_id is None:
        await callback_query.message.reply(MESSAGES['admin_restart'],
                                           reply=False)
        await bot.answer_callback_query(callback_query.id)
        return

    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.id == EventIdHolder.event_id)
        event: Event = event_q.all()[0]

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == EventIdHolder.event_id) \
            .order_by(Enrollment.edit_datetime.desc())
        # get all user and enrollment data
        users_enrolls_list, count = users_enrolls_q.all(), users_enrolls_q.count()
        all_names = [x[0].name_surname for x in users_enrolls_list]

        # header message
        m_h = build_header(event.title,
                           event.id,
                           count,
                           count,
                           all_names)

        # edit header
        try:
            await callback_query.message.edit_text(m_h, reply_markup=keyboard_refresh)
        except MessageNotModified:
            logging.info(f'Message {callback_query.message.message_id} is not modified')

    await bot.answer_callback_query(callback_query.id)


# get media
def media_with_caption(enroll_complete, file_type, file_id, caption):
    if enroll_complete:
        if file_type == 'photo':
            obj = InputMediaPhoto(file_id, caption=caption)
        else:
            obj = InputMediaDocument(file_id, caption=caption)
    else:
        obj = InputMediaDocument(kitty, caption=caption)
    return obj


@dp.callback_query_handler(admin_lambda(),
                           lambda c: c.data in ['back', 'forward', 'rewind_back', 'rewind_forward'],
                           state='*')
async def process_callback_button_scroll(callback_query: types.CallbackQuery):
    if EventIdHolder.event_id is None:
        await callback_query.message.reply(MESSAGES['admin_restart'],
                                           reply=False)
        await bot.answer_callback_query(callback_query.id)
        return

    with session_scope() as session:
        # get all user and enrollment data
        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == EventIdHolder.event_id) \
            .order_by(Enrollment.edit_datetime.desc())
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


# ##################################################################################################################################################
# ##################################################################################################################################################
# ##################################################################################################################################################
# ##################################################################################################################################################


'''User handlers'''


# ##################################################################################################################################################
# ##################################################################################################################################################
# ##################################################################################################################################################
# ##################################################################################################################################################


async def show_event_list_task(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    with session_scope() as session:
        events_q = session.query(Event) \
            .join(User, User.uid == uid) \
            .outerjoin(Enrollment, and_(Enrollment.user_id == User.id, Enrollment.event_id == Event.id)) \
            .filter(Event.status == 1) \
            .filter(or_(Enrollment.id == None, Enrollment.complete == False)) \
            .order_by(Event.edit_datetime.desc())

        if events_q.count() > 0:
            m_text = MESSAGES['show_event_menu']
            events_keyboard = events_reply_keyboard(events_q.all())
            await state.set_state(States.all()[2])
        else:
            m_text = MESSAGES['no_current_events']
            events_keyboard = None

        await message.reply(m_text,
                            reply=False,
                            reply_markup=events_keyboard)


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
            await state.set_state(States.all()[1])  # greet and prompt for name and surname
            await message.reply(MESSAGES['greet_new_user'],
                                parse_mode=ParseMode.MARKDOWN,
                                reply=False)
        else:
            await state.set_state(States.all()[2])  # show event list
            await show_event_list_task(message)


@dp.message_handler(not_admin_lambda(),
                    state=States.STATE_1,
                    content_types=ContentType.TEXT)
async def process_name(message: types.Message):
    uid = message.from_user.id
    with session_scope() as session:
        user_q = session.query(User) \
            .filter(User.uid == uid)
        user: User = user_q.all()[0]

        user.name_surname = message.text

    await message.reply(MESSAGES['pleased_to_meet_you'],
                        parse_mode=ParseMode.MARKDOWN,
                        reply=False)
    await show_event_list_task(message)


@dp.message_handler(not_admin_lambda(),
                    state=States.STATE_2,
                    content_types=ContentType.TEXT)
async def process_event_click(message: types.Message):
    uid = message.from_user.id
    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.title == message.text)
        if event_q.count() == 0:
            await message.reply('Нет такого..',
                                reply=False)
            return
        event: Event = event_q.all()[0]

        user_q = session.query(User) \
            .filter(User.uid == uid)
        user: User = user_q.all()[0]

        enrolled_q = session.query(Enrollment) \
            .join(User) \
            .filter(User.uid == uid) \
            .filter(Enrollment.event_id == event.id)

        if enrolled_q.count() == 0:
            # create enrollment
            enrollment = Enrollment(user_id=user.id,
                                    event_id=event.id,
                                    complete=False) \
                .insert_me(session)
            logging.info(f'enrollment created: {enrollment}')
        else:
            enrollment = enrolled_q.all()[0]

        # build message
        state = dp.current_state(user=uid)
        if enrollment.complete:
            m_text = MESSAGES['registration_exists']
            remove_keyboard = None
        else:
            m_text = MESSAGES['invoice_prompt']
            remove_keyboard = ReplyKeyboardRemove()
            await state.set_state(States.all()[3])
        await message.reply(m_text,
                            parse_mode=ParseMode.MARKDOWN,
                            reply=False,
                            reply_markup=remove_keyboard)


@dp.message_handler(not_admin_lambda(),
                    state=States.STATE_3,
                    content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
async def process_invoice(message: types.Message):
    uid = message.from_user.id

    if message.document is not None:
        invoice_type = 'document'
        file_id = message.document.file_id
    else:
        invoice_type = 'photo'
        file_id = message.photo[-1].file_id

    with session_scope() as session:
        enroll_q = session.query(Enrollment, Event) \
            .join(User) \
            .join(Event) \
            .filter(User.uid == uid) \
            .filter(Enrollment.complete == False)

        enroll, event = enroll_q.all()[0]
        enroll.file_type = invoice_type
        enroll.file_id = file_id
        enroll.complete = True
        enroll.edit_datetime = clock.now()

        state = dp.current_state(user=message.from_user.id)
        await state.set_state(States.all()[3])

        await message.reply(MESSAGES['registration_complete'] + text(event.access_info),
                            parse_mode=ParseMode.MARKDOWN,
                            reply=False)

        await show_event_list_task(message)


@dp.message_handler(not_admin_lambda(),
                    state='*',
                    content_types=ContentType.ANY)
async def chat(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    awaited_state = await state.get_state()
    if awaited_state == States.STATE_1[0]:
        m_text = emojize('Напишите мне, пожалуйста, свою фамилию и имя :)')
    elif awaited_state == States.STATE_2[0]:
        m_text = 'Выберите мероприятие, на которое хотите зарегистрироваться :)'
    elif awaited_state == States.STATE_3[0]:
        m_text = 'Осталось прислать квитанцию! Я верю в тебя! :)'
        # t = text(emojize('На этом всё, дорогой друг! Спасибо, что ты с нами! '
        #                  ':heart: :new_moon_with_face:'))
    else:
        m_text = 'Привет! Для начала, напиши мне /start :)'

    await message.reply(m_text,
                        reply=False)
