import logging

from aiogram import types
from aiogram.types import ParseMode, ContentType
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, text

from app.bot import dp
from app.config import Config
from app.db import session_scope
from app.db.models import User, Event, Enrollment
from app.db.dao import UserDAO, EnrollmentDAO, EventDAO
from app.utils import States, clock

# TODO: remove hardcode
event_id = 1


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    uid = message.from_user.id
    with session_scope() as session:
        user: User = UserDAO.get_by_uid(session, uid)
        if user is None:
            user = User(uid=uid,
                        username=message.from_user.username) \
                .insert_me(session)
            # uid, username
            logging.info(f'user created: {user}')

        # get event
        enroll: Enrollment = EnrollmentDAO.get_by_uid_event_id(session, uid, event_id)
        if enroll is None:
            # create enrollment
            enroll = Enrollment(user_id=user.id,
                                event_id=event_id) \
                .insert_me(session)
            logging.info(f'enrollment created: {enroll}')

        event: Event = EventDAO.get_by_event_id(session, event_id)
        assert event is not None

        # build message
        if enroll.complete:
            m = event.complete_message
        else:
            state = dp.current_state(user=uid)
            if user.name_surname == '':
                m = event.hello_message
                await state.set_state(States.all()[1])
            else:
                # TODO: separate states-messages to its own table
                m = bold('Привет!\n\n') + \
                    bold('Мы продолжаем Соло Лабораторию-недельку :)\n\n') + \
                    'Для регистрации просто пришлите файл или фото с чеком об оплате'
                await state.set_state(States.all()[2])

    await message.reply(m,
                        parse_mode=ParseMode.MARKDOWN,
                        reply=False)


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state=States.STATE_1,
                    content_types=ContentType.TEXT)
async def process_name(message: types.Message):
    uid = message.from_user.id
    with session_scope() as session:
        user: User = UserDAO.get_by_uid(session, uid)
        assert user is not None
        user.name_surname = message.text

    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[2])

    await message.reply('Класс! Теперь пришлите, пожалуйста, квитанцию или фото абонемента.', reply=False)


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state=States.STATE_2,
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
        enroll: Enrollment = EnrollmentDAO.get_by_uid_event_id(session, uid, event_id)
        assert enroll is not None
        enroll.file_type = invoice_type
        enroll.file_id = file_id
        enroll.complete = True
        enroll.edit_datetime = clock.now()

    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[3])

    await message.reply('Спасибо! Вы успешно зарегистрировались. Если вас еще нет в общем канале, вот ссылка:\n'
                        'https://t.me/joinchat/AAAAAFK5EtZ1L7eNAq99Yw', reply=False)


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state='*',
                    content_types=ContentType.ANY)
async def chat(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    awaited_state = await state.get_state()
    if awaited_state == States.STATE_1[0]:
        t = emojize('Напишите мне, пожалуйста, свою фамилию и имя :)')
    elif awaited_state == States.STATE_2[0]:
        t = 'Осталось прислать квитанцию! Я верю в тебя! :)'
    elif awaited_state == States.STATE_3[0]:
        t = text(emojize('На этом всё, дорогой друг! Спасибо, что ты с нами! '
                         ':heart: :new_moon_with_face:'))
    else:
        t = 'Привет! Для начала, напиши мне /start :)'

    await message.reply(t,
                        reply=False)
