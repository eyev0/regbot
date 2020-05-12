from aiogram import types
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile

from app.db import session_scope
from app.db.models import Event
from app.handlers.keyboards import events_reply_keyboard
from app.handlers.messages import MESSAGES

RANDOM_KITTEN_JPG = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Red_Kitten_01.jpg/' \
                    '320px-Red_Kitten_01.jpg'


def media_with_caption(enroll_complete, file_type, file_id, caption):
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


