import logging

from aiogram.utils import executor
from aiogram.utils.exceptions import TerminatedByOtherGetUpdates

from app import dp as dispatcher


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

if __name__ == '__main__':
    try:
        executor.start_polling(dispatcher,
                               on_shutdown=on_shutdown,
                               timeout=20)
    except TerminatedByOtherGetUpdates as e:
        exit(0)
        pass
