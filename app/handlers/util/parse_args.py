import functools

from aiogram import types

from app import dp, bot
from app.handlers.util.states import resolve_state


def mixed_handler_parse_args(func):
    """ Parse args for message and callback_query handlers in one func"""

    @functools.wraps(func)
    async def decorator(obj: types.base.TelegramObject, **partial_data):
        callback_query = None
        if isinstance(obj, types.CallbackQuery):
            callback_query = obj
            message = obj.message
            user_id = callback_query.from_user.id
        elif isinstance(obj, types.Message):
            message = obj
            user_id = message.from_user.id
        else:
            return
        user_state = partial_data.get('state', dp.current_state(user=user_id, chat=user_id))
        kwargs = {
            'user_id': user_id,
            'user_state': user_state,
            'message': message,
            'callback_query': callback_query,
        }
        result = await resolve_state(func)(**kwargs)
        if callback_query:
            await bot.answer_callback_query(callback_query.id)
        return result

    return decorator


def message_handler_parse_args(func):
    @functools.wraps(func)
    async def decorator(message: types.Message, **partial_data):
        user_id = message.from_user.id
        user_state = partial_data.get('state', dp.current_state(user=user_id, chat=user_id))
        kwargs = {
            'user_id': user_id,
            'user_state': user_state,
            'message': message,
        }
        return await resolve_state(func)(**kwargs)

    return decorator


def callback_query_handler_parse_args(func):
    @functools.wraps(func)
    async def decorator(callback_query: types.CallbackQuery, **partial_data):
        message = callback_query.message
        user_id = callback_query.from_user.id
        user_state = partial_data.get('state', dp.current_state(user=user_id, chat=user_id))
        kwargs = {
            'user_id': user_id,
            'user_state': user_state,
            'message': message,
            'callback_query': callback_query,
        }
        result = await resolve_state(func)(**kwargs)
        await bot.answer_callback_query(callback_query.id)
        return result

    return decorator
