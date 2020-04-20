import logging
import os

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook

from config import TOKEN, PROXY_URL

# webhook settings
WEBHOOK_HOST = 'https://de-regbot.herokuapp.com'
WEBHOOK_PATH = '/' + TOKEN
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
try:
    WEBAPP_PORT = int(os.environ.get('PORT', 5000))
except ValueError:
    WEBAPP_PORT = 5000

if os.environ.get('PORT') is not None:
    bot = Bot(token=TOKEN)
else:
    bot = Bot(token=TOKEN, proxy=PROXY_URL)

dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(state='*', commands=['help'])
async def process_help_command(message: types.Message):
    msg = text(bold('Help me!..'))
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN, reply=False)


async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

from admin import *
from user import *

if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        executor.start_polling(dp, reset_webhook=True, on_shutdown=on_shutdown)
