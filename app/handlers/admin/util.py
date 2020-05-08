from aiogram.types import InputMediaPhoto, InputMediaDocument, InputFile

from app import Config


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