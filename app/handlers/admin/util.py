from aiogram import types
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile

from app import Config
from app.db import session_scope
from app.db.models import Event
from app.handlers.keyboards import events_reply_keyboard
from app.handlers.messages import MESSAGES


def media_with_caption(enroll_complete, file_type, file_id, caption):
    if enroll_complete:
        if file_type == 'photo':
            obj = InputMediaPhoto(file_id, caption=caption)
        else:
            obj = InputMediaDocument(file_id, caption=caption)
    else:
        obj = InputMediaDocument(kitty, caption=caption)
    return obj


kitty = InputFile.from_url(Config.RANDOM_KITTEN_JPG, 'Ой! Ещё нет информации о платеже!.jpg')


async def show_menu_task_admin(message: types.Message):
    with session_scope() as session:
        events_q = session.query(Event) \
            .filter(Event.status < 9) \
            .order_by(Event.edit_datetime.desc())

        events_keyboard = events_reply_keyboard(events_q.all(),
                                                admin_mode=True)
        await message.reply(MESSAGES['admin_events_menu'],
                            reply=False,
                            reply_markup=events_keyboard)


