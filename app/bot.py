import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.utils.executor import start_webhook

from app.config import Config

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


if os.environ.get('PORT') is not None:
    bot = Bot(token=Config.TOKEN)
else:
    bot = Bot(token=Config.TOKEN, proxy=Config.PROXY_URL)

dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(Config.WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


from app.handlers.user import *
from app.handlers.admin import *
from app.handlers.common import *

if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        start_webhook(
            dispatcher=dp,
            webhook_path=Config.TOKEN,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=Config.WEBAPP_HOST,
            port=Config.WEBAPP_PORT,
        )
    else:
        executor.start_polling(dp,
                               on_shutdown=on_shutdown,
                               timeout=80)
