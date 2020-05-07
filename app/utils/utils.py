from datetime import datetime

import pytz
from aiogram.utils.helper import Helper, HelperMode, ListItem

from app import Config


class UserStates(Helper):
    mode = HelperMode.snake_case

    STATE_0 = ListItem()
    STATE_1 = ListItem()
    STATE_2 = ListItem()
    STATE_3 = ListItem()


class CreateEventStates(Helper):
    mode = HelperMode.snake_case

    STATE_0 = ListItem()
    STATE_1 = ListItem()
    STATE_2 = ListItem()
    STATE_3 = ListItem()
    STATE_4 = ListItem()
    STATE_5 = ListItem()


class EventIdHolder(object):
    event_id = None


class WrappingListIterator(object):

    obj = None

    def __init__(self):
        self.pos = 0
        self.__class__.obj = self

    @classmethod
    def get_obj(cls):
        if cls.obj is None:
            cls.obj = cls()
        return cls.obj

    def fetch(self, list_, direction=None):
        if len(list_) == 0:
            return None
        if direction is not None:
            if direction[:6] != 'rewind':
                self.pos += (1 if direction == 'forward' else -1)
            else:
                self.pos = (len(list_) - 1 if direction[7:] == 'forward' else 0)
        # wrap around list
        if self.pos > len(list_) - 1:
            self.pos = 0
        elif self.pos < 0:
            self.pos = len(list_) - 1

        return list_[self.pos]


clock = datetime(2020, 1, 1, tzinfo=pytz.timezone('Europe/Moscow'))


def admin_lambda():
    return lambda m: m.from_user.id in Config.admin_ids


def not_admin_lambda():
    return lambda m: m.from_user.id not in Config.admin_ids
