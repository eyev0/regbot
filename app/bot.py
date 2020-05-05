import logging
import os

from aiogram.utils import executor
from aiogram.utils.executor import start_webhook

from app import dp as dispatcher, bot, Config


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

if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        start_webhook(
            dispatcher=dispatcher,
            webhook_path=Config.TOKEN,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=Config.WEBAPP_HOST,
            port=Config.WEBAPP_PORT,
        )
    else:
        executor.start_polling(dispatcher,
                               on_shutdown=on_shutdown,
                               timeout=20)
