import logging
from datetime import datetime
import argparse

import pytz
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from app.config import Config
from app.storage_util import FSMContextFactory

clock = datetime(2020, 1, 1, tzinfo=pytz.timezone('Europe/Moscow'))

parser = argparse.ArgumentParser(description='Power up regbot. Use -t for testing')
parser.add_argument('-t', '--test', dest='test_env',
                    action='store_true', default=False)
parser.add_argument('-c', '--container', dest='container',
                    action='store_true', default=False)
args = parser.parse_args()
config = Config(args.container, args.test_env)

logging.basicConfig(filename=config.log_path,
                    format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

bot = Bot(token=config.TOKEN, proxy=config.PROXY_URL)
dp = Dispatcher(bot, storage=JSONStorage(config.FSMstorage_path))
dp.middleware.setup(LoggingMiddleware())

navigation_context = FSMContextFactory(JSONStorage(config.navigation_storage))

import app.handlers
