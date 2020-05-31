import logging
import signal
import sys

import aiogram
from aiogram.utils import executor

from app import dp as dispatcher, config
from app.log import trace_async, trace


@trace_async
async def on_startup(dp: aiogram.Dispatcher):
    if config.app.webhook_mode:
        await trace_async(dp.bot.set_webhook)(config.webhook.url)

    me = await dp.bot.get_me()
    logging.warning(f'Powering up @{me["username"]}')


@trace_async
async def on_shutdown(dp: aiogram.Dispatcher):
    logging.warning('Shutting down..')

    # Close DB connection (if used)
    await trace_async(dp.storage.close)()
    await trace_async(dp.storage.wait_closed)()

    if config.app.webhook_mode:
        await trace_async(dp.bot.delete_webhook)()

    logging.warning('Bye!')


@trace
def terminate(signalnum, frame):
    logging.warning(f'!! received {signalnum}, terminating the process')
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminate)
    if config.app.webhook_mode:
        executor.start_webhook(dispatcher=dispatcher,
                               webhook_path=config.webhook.path,
                               on_startup=on_startup,
                               on_shutdown=on_shutdown,
                               skip_updates=False,
                               host=config.webhook.webapp_host,
                               port=config.webhook.webapp_port)
    else:
        executor.start_polling(dispatcher,
                               on_startup=on_startup,
                               on_shutdown=on_shutdown,
                               timeout=20)
