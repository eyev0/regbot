import logging
from datetime import datetime

import pytz
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from app.config import Config

clock = datetime(2020, 1, 1, tzinfo=pytz.timezone('Europe/Moscow'))

logging.basicConfig(filename=Config.log_path,
                    format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

bot = Bot(token=Config.TOKEN, proxy=Config.PROXY_URL)
dp = Dispatcher(bot, storage=JSONStorage(Config.FSMstorage_path))
dp.middleware.setup(LoggingMiddleware())

import app.handlers
