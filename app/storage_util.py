from aiogram import types
from aiogram.dispatcher import FSMContext


class FSMContextFactory(object):

    def __init__(self, storage):
        self.storage = storage

    def get_fsm_context(self, user, chat=None) -> FSMContext:
        if chat is None:
            chat_obj = types.Chat.get_current()
            chat = chat_obj.id if chat_obj else None
        if user is None:
            user_obj = types.User.get_current()
            user = user_obj.id if user_obj else None

        return FSMContext(storage=self.storage, chat=chat, user=user)

    async def save(self, user, key, value):
        obj = self.get_fsm_context(user, chat=user)
        map_ = await obj.get_data() or {}
        map_[str(key)] = value
        await obj.set_data(map_)

    async def get(self, user, key):
        obj = self.get_fsm_context(user, chat=user)
        map_ = await obj.get_data() or {}
        return map_.get(str(key), None)
