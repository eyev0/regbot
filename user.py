import shelve

from aiogram import types
# from aiogram.dispatcher import filters
from aiogram.types import ParseMode, ContentType
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, text

from bot import dp, logging
from config import file, admin_ids
from utils import States, User, Payment


@dp.message_handler(lambda m: m.from_user.id not in admin_ids,
                    state='*',
                    commands=['start'])
async def process_start_command(message: types.Message):
    u_id = message.from_user.id

    with shelve.open(filename=file) as db:
        user = db.get(str(u_id), User(user_id=u_id,
                                      username=message.from_user.username))
        if user.reg_passed:
            await message.reply(bold('Вы уже зарегистрировались! Ура!'),
                                parse_mode=ParseMode.MARKDOWN)
            return
        else:
            db[str(u_id)] = user

    logging.info(f'user created: {user}')
    state = dp.current_state(user=u_id)
    await state.set_state(States.all()[1])

    await message.reply(bold('Привет!\n\n') +
                        bold('Чтобы зарегистрироваться на Соло Лабораторию: \n\n') +
                        '    1. Напишите свою фамилию и имя\n'
                        '    2. Пришлите файл или фото с чеком об оплате '
                        'или фото твоего абонемента МСДК'
                        '(после регистрации я напишу вам лично, как и что отметить в абонементе)\n\n',
                        parse_mode=ParseMode.MARKDOWN,
                        reply=False)


@dp.message_handler(lambda m: m.from_user.id not in admin_ids,
                    #
                    # filters.Regexp(regexp='[a-zA-Zа-яА-Я\']+ [a-zA-Zа-яА-Я\']+'),
                    state=States.STATE_1,
                    content_types=ContentType.TEXT)
async def save_name_surname(message: types.Message):
    u_id = message.from_user.id
    with shelve.open(filename=file) as db:
        user: User = db[str(u_id)]
        user.name_surname = message.text
        db[str(u_id)] = user

    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[2])

    await message.reply('Класс! Теперь пришлите, пожалуйста, квитанцию или фото абонемента.', reply=False)


@dp.message_handler(lambda m: m.from_user.id not in admin_ids,
                    state=States.STATE_2,
                    content_types=[ContentType.PHOTO])
async def save_payment_photo(message: types.Message):
    await save_payment(message, payment_type='photo')


@dp.message_handler(lambda m: m.from_user.id not in admin_ids,
                    state=States.STATE_2,
                    content_types=[ContentType.DOCUMENT])
async def save_payment_document(message: types.Message):
    await save_payment(message, payment_type='document')


async def save_payment(message: types.Message, payment_type=None):
    u_id = message.from_user.id

    with shelve.open(filename=file) as db:
        user: User = db[str(u_id)]
        if payment_type == 'photo':
            user.payment = Payment(payment_type, message.photo[-1].file_id)
        else:
            user.payment = Payment(payment_type, message.document.file_id)
        user.reg_passed = True
        db[str(u_id)] = user

    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[3])

    await message.reply('Спасибо! Вы успешно зарегистрировались. Если вас еще нет в общем канале, вот ссылка:\n'
                        'https://t.me/joinchat/AAAAAFK5EtZ1L7eNAq99Yw', reply=False)


@dp.message_handler(lambda m: m.from_user.id not in admin_ids,
                    state=States.STATE_3,
                    content_types=ContentType.ANY)
async def done(message: types.Message):
    await message.reply(text(emojize('На этом всё, дорогой друг! Спасибо, что ты с нами! '
                                     ':heart: :new_moon_with_face:')),
                        reply=False)


@dp.message_handler(lambda m: m.from_user.id not in admin_ids,
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
