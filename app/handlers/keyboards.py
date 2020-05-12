from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove


async def send_remove_reply_keyboard(message: types.Message):
    remove_keyboard_stub: types.Message = await message.reply('...',
                                                              reply=False,
                                                              reply_markup=ReplyKeyboardRemove())
    await remove_keyboard_stub.delete()


def events_reply_keyboard(events_list, admin_mode=False, archived=False):
    max_buttons_in_row = 1
    keyboard = ReplyKeyboardMarkup()
    if len(events_list) > 0:
        i = 0
        row_list = []
        for event in events_list:
            button = KeyboardButton(event.title)
            if len(row_list) == i:
                row_list.append([])
            row_list[i].append(button)
            if len(row_list[i]) == max_buttons_in_row:
                i += 1
        for row in row_list:
            keyboard.row(*row)

    if admin_mode:
        if archived:
            keyboard.row(button_back_to_events)
        else:
            keyboard.row(button_create_new)
            keyboard.row(button_view_archive)

    return keyboard


button_create_new = KeyboardButton('Создать новое')
button_view_archive = KeyboardButton('Архив')

button_back_to_events = KeyboardButton('Назад')

button_cancel = KeyboardButton('Отмена')
keyboard_cancel = ReplyKeyboardMarkup().row(button_cancel)

# Основное меню
button_view_enrolls = KeyboardButton('Список регистраций')
button_info = KeyboardButton('Инфа мероприятия')
button_change_status = KeyboardButton('Изменить статус ивента')
button_publish = KeyboardButton('Отправить уведомление юзерам')
keyboard_admin_menu = ReplyKeyboardMarkup()
keyboard_admin_menu.row(button_view_enrolls)
keyboard_admin_menu.row(button_info)
keyboard_admin_menu.row(button_change_status)
keyboard_admin_menu.row(button_publish)
keyboard_admin_menu.row(button_back_to_events)

# Изменить статус ивента
button_status_0 = KeyboardButton('0 - не опубликованно')
button_status_1 = KeyboardButton('1 - регистрация открыта')
button_status_9 = KeyboardButton('9 - регистрация закрыта')
button_status_10 = KeyboardButton('10 - архивировано')
button_back_to_event_menu = KeyboardButton('Назад')
keyboard_change_status = ReplyKeyboardMarkup()
keyboard_change_status.row(button_status_0)
keyboard_change_status.row(button_status_1)
keyboard_change_status.row(button_status_9)
keyboard_change_status.row(button_status_10)
keyboard_change_status.row(button_back_to_event_menu)

# Просмотр регистраций
button_refresh = InlineKeyboardButton('Обновить', callback_data='refresh')
keyboard_refresh = InlineKeyboardMarkup().row(button_refresh)

button_rewind_back = InlineKeyboardButton('<<', callback_data='rewind_back')
button_back = InlineKeyboardButton('<', callback_data='back')
button_forward = InlineKeyboardButton('>', callback_data='forward')
button_rewind_forward = InlineKeyboardButton('>>', callback_data='rewind_forward')
keyboard_scroll = InlineKeyboardMarkup().row(
    button_rewind_back, button_back,
    button_forward, button_rewind_forward
)
