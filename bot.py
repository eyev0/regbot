import logging

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

from config import TOKEN, PROXY_URL

bot = Bot(token=TOKEN, proxy=PROXY_URL)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(state='*', commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(bold('Help me!..'))
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN, reply=False)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


from admin import *
from user import *

if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
