from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

button_rewind_back = InlineKeyboardButton('<<', callback_data='rewind_back')
button_back = InlineKeyboardButton('<', callback_data='back')
button_check = InlineKeyboardButton('✔️',  callback_data='check')
button_forward = InlineKeyboardButton('>', callback_data='forward')
button_rewind_forward = InlineKeyboardButton('>>', callback_data='rewind_forward')

keyboard_scroll = InlineKeyboardMarkup().row(
    button_back, button_forward
).row(
    button_rewind_back, button_check, button_rewind_forward
)

button_refresh = InlineKeyboardButton('Обновить', callback_data='refresh')
keyboard_refresh = InlineKeyboardMarkup().row(button_refresh)

#
# keyboard = ReplyKeyboardMarkup().row(
#     button1, button2
# )
# reply_markup=ReplyKeyboardRemove(),


####################
