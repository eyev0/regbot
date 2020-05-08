from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.helper import Helper, HelperMode, ListItem

from app import Config


def admin_lambda():
    return lambda m: m.from_user.id in Config.admin_ids


def not_admin_lambda():
    return lambda m: m.from_user.id not in Config.admin_ids


async def send_remove_reply_keyboard(message: types.Message):
    remove_keyboard_stub: types.Message = await message.reply('...',
                                                              reply=False,
                                                              reply_markup=ReplyKeyboardRemove())
    await remove_keyboard_stub.delete()


class UserStates(Helper):
    mode = HelperMode.snake_case

    USER_STATE_0 = ListItem()
    USER_STATE_1 = ListItem()
    USER_STATE_2 = ListItem()
    USER_STATE_3 = ListItem()


class AdminMenuStates(Helper):
    mode = HelperMode.snake_case

    ADMIN_MENU_STATE_0 = ListItem()


class CreateEventStates(Helper):
    mode = HelperMode.snake_case

    CREATE_EVENT_STATE_0 = ListItem()
    CREATE_EVENT_STATE_1 = ListItem()
    CREATE_EVENT_STATE_2 = ListItem()
    CREATE_EVENT_STATE_3 = ListItem()