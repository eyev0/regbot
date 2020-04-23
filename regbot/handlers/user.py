import logging

from aiogram import types
from aiogram.types import ParseMode, ContentType
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, text

from regbot.bot import dp
from regbot.config import Config
from regbot.db import session_scope, User, create_user, clock
from regbot.utils import States


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    u_id = message.from_user.id
    with session_scope() as session:
        user: User = session.query(User).filter_by(user_id=u_id).all()
        if user is None:
            user = create_user(session, u_id)

        # build message
        if user.is_registered:
            m = bold('Вы уже зарегистрировались! Ура!')
        else:
            logging.info(f'user created: {user}')
            m = bold('Привет!\n\n') + \
                bold('Чтобы зарегистрироваться на Соло Лабораторию: \n\n') + \
                '    1. Напишите свою фамилию и имя\n' \
                '    2. Пришлите файл или фото с чеком об оплате ' \
                'или фото твоего абонемента МСДК' \
                '(после регистрации я напишу вам лично, как и что отметить в абонементе)\n\n'

    state = dp.current_state(user=u_id)
    await state.set_state(States.all()[1])

    await message.reply(m,
                        parse_mode=ParseMode.MARKDOWN,
                        reply=False)


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state=States.STATE_1,
                    content_types=ContentType.TEXT)
async def process_name(message: types.Message):
    u_id = message.from_user.id
    with session_scope() as session:
        user: User = session.query(User).filter_by(user_id=u_id).all()
        user.name_surname = message.text

    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[2])

    await message.reply('Класс! Теперь пришлите, пожалуйста, квитанцию или фото абонемента.', reply=False)


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state=States.STATE_2,
                    content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
async def process_invoice(message: types.Message):
    u_id = message.from_user.id
    if message.photo is not None:
        payment_type = 'photo'
        file_id = message.photo[-1].file_id
    else:
        payment_type = 'document'
        file_id = message.document.file_id

    with session_scope() as session:
        user: User = session.query(User).filter_by(user_id=u_id).all()
        user.file_type = payment_type
        user.file_id = file_id
        user.is_registered = True
        user.edit_datetime = clock.now()
    # with shelve.open(filename=file) as db:
    #     user: User = db[str(u_id)]
    #     if payment_type == 'photo':
    #         user.payment = Payment(payment_type, message.photo[-1].file_id)
    #     else:
    #         user.payment = Payment(payment_type, message.document.file_id)
    #     user.reg_passed = True
    #     user.edit_datetime = str(clock.now())
    #     db[str(u_id)] = user

    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[3])

    await message.reply('Спасибо! Вы успешно зарегистрировались. Если вас еще нет в общем канале, вот ссылка:\n'
                        'https://t.me/joinchat/AAAAAFK5EtZ1L7eNAq99Yw', reply=False)


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state=States.STATE_3,
                    content_types=ContentType.ANY)
async def done(message: types.Message):
    await message.reply(text(emojize('На этом всё, дорогой друг! Спасибо, что ты с нами! '
                                     ':heart: :new_moon_with_face:')),
                        reply=False)


@dp.message_handler(lambda m: m.from_user.id not in Config.admin_ids,
                    state=States.all())
async def incorrect_input(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    if await state.get_state() == States.STATE_1[0]:
        t = emojize('Напишите мне, пожалуйста, свою фамилию и имя :)')
    elif await state.get_state() == States.STATE_2[0]:
        t = 'Осталось только прислать квитанцию или абонемент! Я верю в тебя! :)'
    else:
        assert False
    await message.reply(t,
                        reply=False)
