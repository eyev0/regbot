from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove

# keyboard_admin_menu = ReplyKeyboardMarkup()

button_view_enrolls = KeyboardButton('Список регистраций')
button_create_new = KeyboardButton('Создать новый ивент')
button_change_status = KeyboardButton('Изменить статус ивента')
button_publish = KeyboardButton('Отправить уведомление юзерам')
keyboard_admin_menu = ReplyKeyboardMarkup()
keyboard_admin_menu.row(button_view_enrolls)
keyboard_admin_menu.row(button_create_new)
keyboard_admin_menu.row(button_change_status)
keyboard_admin_menu.row(button_publish)

# KEYBOARDS = {
#     AdminMenuStates.ADMIN_MENU_STATE_0: keyboard_admin_menu,
# }

##


button_rewind_back = InlineKeyboardButton('<<', callback_data='rewind_back')
button_back = InlineKeyboardButton('<', callback_data='back')
button_check = InlineKeyboardButton('✔️', callback_data='check')
button_forward = InlineKeyboardButton('>', callback_data='forward')
button_rewind_forward = InlineKeyboardButton('>>', callback_data='rewind_forward')

keyboard_scroll = InlineKeyboardMarkup().row(
    button_back, button_forward
).row(
    button_rewind_back, button_check, button_rewind_forward
)

button_refresh = InlineKeyboardButton('Обновить', callback_data='refresh')
keyboard_refresh = InlineKeyboardMarkup().row(button_refresh)

max_buttons_in_row = 1


def events_reply_keyboard(events_list):
    if len(events_list) == 0:
        return None
    i = 0
    row_list = []
    for event in events_list:
        button = KeyboardButton(event.title)
        if len(row_list) == i:
            row_list.append([])
        row_list[i].append(button)
        if len(row_list[i]) == max_buttons_in_row:
            i += 1

    keyboard = ReplyKeyboardMarkup()
    for row in row_list:
        keyboard.row(*row)

    return keyboard


async def send_reply_keyboard(message: types.Message, state):
    send_keyboard_stub: types.Message = await message.reply('...',
                                                            reply=False,
                                                            reply_markup=KEYBOARDS[state])
    await send_keyboard_stub.delete()


async def send_remove_reply_keyboard(message: types.Message):
    remove_keyboard_stub: types.Message = await message.reply('...',
                                                              reply=False,
                                                              reply_markup=ReplyKeyboardRemove())
    await remove_keyboard_stub.delete()
