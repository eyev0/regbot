import logging

from aiogram import types
from aiogram.types import InputMediaDocument
from aiogram.utils.exceptions import MessageNotModified, BadRequest

from app import dp, bot
from app.db import session_scope
from app.db.models import Event, User, Enrollment
from app.db.util import WrappingListIterator
from app.handlers import AdminMenuStates
from app.handlers.admin.util import media_with_caption, kitty
from app.handlers.keyboards import keyboard_refresh, keyboard_scroll
from app.handlers.messages import build_header, build_caption, MESSAGES


@dp.callback_query_handler(lambda c: c.data in ['refresh'],
                           state=AdminMenuStates.ADMIN_MENU_STATE_1)
async def process_callback_button_refresh_header(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    state = dp.current_state(user=uid)
    state_data = await state.get_data()
    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.id == state_data['event_id'])
        event: Event = event_q.all()[0]

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == state_data['event_id']) \
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


@dp.callback_query_handler(lambda c: c.data in ['back', 'forward', 'rewind_back', 'rewind_forward'],
                           state=AdminMenuStates.ADMIN_MENU_STATE_1)
async def process_callback_button_scroll(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    state = dp.current_state(user=uid)
    state_data = await state.get_data()
    with session_scope() as session:
        # get all user and enrollment data
        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == state_data['event_id']) \
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


@dp.callback_query_handler(state='*')
async def process_callback_restart_prompt(callback_query: types.CallbackQuery):
    await callback_query.message.reply(MESSAGES['admin_restart'],
                                       reply=False)
    await bot.answer_callback_query(callback_query.id)
    return
