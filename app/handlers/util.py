from aiogram.utils.helper import Helper, HelperMode, ListItem

from app import config


def admin_lambda():
    return lambda m: m.from_user.id in config.admin_ids


def not_admin_lambda():
    return lambda m: m.from_user.id not in config.admin_ids


class UserStates(Helper):
    mode = HelperMode.snake_case

    USER_STATE_0 = ListItem()
    USER_STATE_1 = ListItem()
    USER_STATE_2 = ListItem()
    USER_STATE_3 = ListItem()


class AdminMenuStates(Helper):
    mode = HelperMode.snake_case

    ADMIN_MENU_STATE_0 = ListItem()
    ADMIN_MENU_STATE_1 = ListItem()
    ADMIN_MENU_STATE_2 = ListItem()
    ADMIN_MENU_STATE_3 = ListItem()
    ADMIN_MENU_STATE_4 = ListItem()


class CreateEventStates(Helper):
    mode = HelperMode.snake_case

    CREATE_EVENT_STATE_0 = ListItem()
    CREATE_EVENT_STATE_1 = ListItem()
    CREATE_EVENT_STATE_2 = ListItem()
    CREATE_EVENT_STATE_3 = ListItem()
