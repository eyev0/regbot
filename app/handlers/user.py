import logging

from aiogram import types
from aiogram.types import ParseMode, ContentType
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, text

from app.bot import dp
from app.config import Config
from app.db import session_scope
from app.db.models import User
from app.db.dao import UserDAO
from app.utils import States, clock


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    uid = message.from_user.id
    with session_scope() as session:
        user: User = UserDAO.get_by_uid(session, uid)
        if user is None:
            user = User(user_id=uid,
                        username=message.from_user.username) \
                .insert_me(session)
            # uid, username
            logging.info(f'user created: {user}')

        # build message
        if user.is_registered:
            m = bold('Вы уже зарегистрировались! Ура!')
        else:
            m = bold('Привет!\n\n') + \
                bold('Чтобы зарегистрироваться на Соло Лабораторию: \n\n') + \
                '    1. Напишите свою фамилию и имя\n' \
                '    2. Пришлите файл или фото с чеком об оплате ' \
                'или фото твоего абонемента МСДК' \
                '(после регистрации я напишу вам лично, как и что отметить в абонементе)\n\n'
            state = dp.current_state(user=uid)
            await state.set_state(States.all()[1])

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
        user: User = UserDAO.get_by_uid(session, uid)
        assert user is not None
        user.file_type = invoice_type
        user.file_id = file_id
        user.is_registered = True
        user.edit_datetime = clock.now()

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
        t = 'Осталось только прислать квитанцию или абонемент! Я верю в тебя! :)'
    elif awaited_state == States.STATE_3[0]:
        t = text(emojize('На этом всё, дорогой друг! Спасибо, что ты с нами! '
                         ':heart: :new_moon_with_face:'))
    else:
        t = 'Привет! Для начала, напиши мне /start :)'

    await message.reply(t,
                        reply=False)
