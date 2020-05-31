import functools

from aiogram.dispatcher import FSMContext
from aiogram.utils.helper import Helper, HelperMode, ListItem


class UserStates(Helper):
    mode = HelperMode.snake_case

    USER_STATE_0 = ListItem()
    USER_STATE_1 = ListItem()
    USER_STATE_2 = ListItem()
    USER_STATE_3 = ListItem()


class MenuStates(Helper):
    mode = HelperMode.snake_case

    MENU_STATE_0 = ListItem()  # 0
    MENU_STATE_1_EVENT = ListItem()  # 1
    MENU_STATE_2_ARCHIVE = ListItem()  # 2


class CreateEventStates(Helper):
    mode = HelperMode.snake_case

    CREATE_EVENT_STATE_0 = ListItem()
    CREATE_EVENT_STATE_1 = ListItem()
    CREATE_EVENT_STATE_2 = ListItem()
    CREATE_EVENT_STATE_3 = ListItem()


class ChangeStatusStates(Helper):
    mode = HelperMode.snake_case

    CHANGE_STATUS_STATE_0 = ListItem()
    CHANGE_STATUS_STATE_1 = ListItem()


class PublishStates(Helper):
    mode = HelperMode.snake_case

    PUBLISH_STATE_0 = ListItem()
    PUBLISH_STATE_1 = ListItem()


def resolve_state(func):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        result = await func(*args, **kwargs)

        user_state: FSMContext = kwargs.get('user_state', None)
        if user_state is not None:
            await user_state.set_state(result)
        return result

    return decorator
