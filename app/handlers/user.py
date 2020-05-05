import logging

from aiogram import types
from aiogram.types import ParseMode, ContentType, ReplyKeyboardRemove
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text
from sqlalchemy import or_, and_

from app import dp
from app.config import Config
from app.const.messages import MESSAGES
from app.db import session_scope
from app.db.models import User, Enrollment, Event
from app.handlers.utils.keyboards import events_reply_keyboard
from app.handlers.utils.utils import States, clock


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


@dp.message_handler(lambda m: m.from_user.id in Config.admin_ids,
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


@dp.message_handler(lambda m: m.from_user.id in Config.admin_ids,
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


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
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


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
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


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
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


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
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


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
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
