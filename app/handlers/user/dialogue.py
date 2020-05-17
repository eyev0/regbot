import logging

from aiogram import types
from aiogram.types import ReplyKeyboardRemove, ParseMode, ContentType
from aiogram.utils.markdown import text

from app import dp, clock, user_notify_context, bot
from app.db import session_scope
from app.db.models import Event, User, Enrollment
from app.handlers.user import show_event_list_task
from app.handlers.keyboards import button_enroll
from app.handlers.messages import MESSAGES
from app.handlers.states import UserStates


@dp.message_handler(state=UserStates.USER_STATE_1,
                    content_types=ContentType.TEXT)
async def name(message: types.Message):
    uid = message.from_user.id
    with session_scope() as session:
        user = User(uid=uid,
                    username=message.from_user.username,
                    full_name=message.text) \
            .insert_me(session)
        logging.info(f'user created: {user}')

    await message.reply(MESSAGES['pleased_to_meet_you'],
                        parse_mode=ParseMode.MARKDOWN,
                        reply=False)
    await show_event_list_task(uid)


@dp.callback_query_handler(lambda c: c.data in [button_enroll.callback_data],
                           state='*')
@dp.message_handler(state=UserStates.USER_STATE_2,
                    content_types=ContentType.TEXT)
async def enroll_event(obj: types.base.TelegramObject):
    callback = False
    callback_query = None
    if isinstance(obj, types.CallbackQuery):
        callback = True
        callback_query = obj
        message = obj.message
        uid = callback_query.from_user.id
    elif isinstance(obj, types.Message):
        message = obj
        uid = message.from_user.id
    else:
        return
    state = dp.current_state(user=uid)
    with session_scope() as session:
        if callback:
            event_id = await user_notify_context.get(user=uid, key=message.message_id)
        else:
            event_q = session.query(Event) \
                .filter(Event.title == message.text)
            if event_q.count() == 0:
                return
            event: Event = event_q.all()[0]
            event_id = event.id
        await state.set_data({'event_id': event_id})

        user_q = session.query(User) \
            .filter(User.uid == uid)
        user: User = user_q.all()[0]

        enrolled_q = session.query(Enrollment) \
            .join(User) \
            .filter(User.uid == uid) \
            .filter(Enrollment.event_id == event_id)

        if enrolled_q.count() == 0:
            # create enrollment
            enrollment = Enrollment(user_id=user.id,
                                    event_id=event_id,
                                    complete=False) \
                .insert_me(session)
            logging.info(f'enrollment created: {enrollment}')
        else:
            enrollment = enrolled_q.all()[0]

        # build message
        if enrollment.complete:
            m_text = MESSAGES['registration_exists']
            remove_keyboard = None
        else:
            m_text = MESSAGES['invoice_prompt']
            remove_keyboard = ReplyKeyboardRemove()
            await state.set_state(UserStates.all()[3])
        await message.reply(m_text,
                            parse_mode=ParseMode.MARKDOWN,
                            reply=False,
                            reply_markup=remove_keyboard)
        if callback:
            await bot.answer_callback_query(callback_query.id)


@dp.message_handler(state=UserStates.USER_STATE_3,
                    content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
async def invoice(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    state_data = await state.get_data() or {}

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
            .filter(Event.id == state_data['event_id'])

        enroll, event = enroll_q.all()[0]
        enroll.file_type = invoice_type
        enroll.file_id = file_id
        enroll.complete = True
        enroll.edit_datetime = clock.now()
        logging.info(f'enrollment updated! got invoice: {enroll}')

        state = dp.current_state(user=message.from_user.id)
        await state.set_state(None)
        await state.set_data({})

        complete_message = await message.reply(MESSAGES['registration_complete'] + text(event.access_info),
                                               parse_mode=ParseMode.MARKDOWN,
                                               reply=False)

        await show_event_list_task(message.from_user.id,
                                   edit_markup=True,
                                   message=complete_message)


@dp.message_handler(state=UserStates.all().append(None),
                    content_types=ContentType.ANY)
async def chat(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    current_state = await state.get_state()
    m_text = MESSAGES['help_' + str(current_state)]
    await message.reply(m_text,
                        reply=False)
