import logging

from aiogram import types
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile
from aiogram.utils.exceptions import BadRequest, MessageNotModified

from app import bot
from app.db import session_scope
from app.db.models import Event, User, Enrollment
from app.handlers import enrollment_str, keyboard_scroll, full_names_list_str, keyboard_refresh, event_str
from app.handlers.keyboards import events_reply_keyboard, event_menu_keyboard
from app.handlers.messages import MESSAGES

RANDOM_KITTEN_JPG = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Red_Kitten_01.jpg/' \
                    '320px-Red_Kitten_01.jpg'


def get_media_obj(enroll_complete, file_type, file_id, caption):
    if enroll_complete:
        if file_type == 'photo':
            obj = InputMediaPhoto(file_id, caption=caption)
        else:
            obj = InputMediaDocument(file_id, caption=caption)
    else:
        obj = InputMediaDocument(kitty, caption=caption)
    return obj


kitty = InputFile.from_url(RANDOM_KITTEN_JPG, 'Ой! Ещё нет информации о платеже!.jpg')


async def show_events_task_admin(message: types.Message,
                                 archived=False):
    with session_scope() as session:
        events_q = session.query(Event)
        if archived:
            m_text = MESSAGES['admin_archive']
            events_q = events_q.filter(Event.status == 10)
        else:
            m_text = MESSAGES['admin_events']
            events_q = events_q.filter(Event.status <= 9)
        events_q = events_q.order_by(Event.edit_datetime.desc())

        events_keyboard = events_reply_keyboard(events_q.all(),
                                                admin_mode=True,
                                                archived=archived)
        await message.reply(m_text,
                            reply=False,
                            reply_markup=events_keyboard)


async def send_enrollment_message(message: types.Message,
                                  user: User,
                                  enrollment: Enrollment,
                                  edit=False) -> types.Message:
    m_b = enrollment_str(user.uid,
                         user.username,
                         user.full_name,
                         enrollment.complete,
                         enrollment.edit_datetime)
    if edit:
        try:
            await message.edit_media(get_media_obj(enrollment.complete,
                                                   enrollment.file_type,
                                                   enrollment.file_id,
                                                   m_b),
                                     reply_markup=keyboard_scroll)
        except MessageNotModified:
            logging.info(f'Message {message.message_id} is not modified')
        except BadRequest:
            # can't send media
            await message.edit_media(InputMediaDocument(kitty, caption=m_b),
                                     reply_markup=keyboard_scroll)
        finally:
            result = message
    else:
        if enrollment.complete:
            try:
                if enrollment.file_type == 'photo':
                    result = await bot.send_photo(message.chat.id,
                                                  photo=enrollment.file_id,
                                                  caption=m_b,
                                                  reply_markup=keyboard_scroll)
                else:
                    result = await bot.send_document(message.chat.id,
                                                     document=enrollment.file_id,
                                                     caption=m_b,
                                                     reply_markup=keyboard_scroll)
            except BadRequest:
                # can't send media
                result = await bot.send_document(message.chat.id,
                                                 document=kitty,
                                                 caption=m_b,
                                                 reply_markup=keyboard_scroll)
        else:
            result = await bot.send_document(message.chat.id,
                                             document=kitty,
                                             caption=m_b,
                                             reply_markup=keyboard_scroll)
    return result


async def send_user_list_message(message: types.Message,
                                 event: Event,
                                 names_list,
                                 edit=False) -> types.Message:
    m_h = event_str(event.title,
                    Event.status_map[event.status],
                    len(names_list)) + full_names_list_str(names_list)
    if edit:
        try:
            await message.edit_text(m_h, reply_markup=keyboard_refresh)
        except MessageNotModified:
            logging.info(f'Message {message.message_id} is not modified')
        finally:
            result = message
    else:
        result = await message.reply(m_h,
                                     reply=False,
                                     reply_markup=keyboard_refresh)
    return result


async def send_event_message(message: types.Message,
                             event: Event,
                             count: int,
                             edit=False) -> types.Message:
    m_h = event_str(event.title,
                    Event.status_map[event.status],
                    count)
    if edit:
        try:
            await message.edit_text(m_h,
                                    reply_markup=event_menu_keyboard(event.status))
        except MessageNotModified:
            logging.info(f'Message {message.message_id} is not modified')
        finally:
            result = message
    else:
        result = await message.reply(m_h,
                                     reply=False,
                                     reply_markup=event_menu_keyboard(event.status))
    return result
