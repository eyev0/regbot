import shelve
from datetime import datetime

from aiogram.utils.helper import Helper, HelperMode, ListItem

from config import file


class States(Helper):
    mode = HelperMode.snake_case

    STATE_0 = ListItem()
    STATE_1 = ListItem()
    STATE_2 = ListItem()
    STATE_3 = ListItem()
    STATE_4 = ListItem()
    STATE_5 = ListItem()


class Payment(object):
    def __init__(self,
                 file_type=None,
                 file_id=None):
        self.file_type = file_type
        self.file_id = file_id


class User(object):

    def __init__(self,
                 user_id=0,
                 username='',
                 name_surname='',
                 reg_passed=False,
                 payment=None):
        self.user_id = user_id
        self.username = username
        self.name_surname = name_surname
        self.reg_passed = reg_passed
        self.payment = payment
        self.time_created = str(datetime.utcnow())

    def __repr__(self):
        return f'User(user_id={self.user_id}, ' \
               f'username={self.username}, ' \
               f'name_surname={self.name_surname}, ' \
               f'reg_passed={self.reg_passed}, ' \
               f'payment={self.payment}, ' \
               f'time_created={self.time_created})'


class UserDbAccessObject(object):

    def __init__(self):
        self.pos = 0
        self.user = None

    def reset_pos(self):
        self.pos = 0

    @staticmethod
    def size():
        with shelve.open(filename=file) as db:
            return len(db)

    def current(self):
        with shelve.open(filename=file) as db:
            if self.pos > len(db) - 1:
                self.pos = len(db) - 1
            ids = [(x, db[x].time_created) for x in db.keys()]
            ids.sort(key=lambda x: x[1], reverse=True)
            if len(ids) == 0:
                return None
            self.user: User = db.get(ids[self.pos][0])
        return self.user

    def next(self):
        with shelve.open(filename=file) as db:
            if self.pos >= len(db) - 1:
                self.pos = 0
            else:
                self.pos += 1
            ids = [(x, db[x].time_created) for x in db.keys()]
            ids.sort(key=lambda x: x[1], reverse=True)
            if len(ids) == 0:
                return None
            self.user: User = db.get(ids[self.pos][0])
            return self.user

    def prev(self):
        with shelve.open(filename=file) as db:
            if self.pos == 0 or self.pos > len(db) - 1:
                self.pos = len(db) - 1
            else:
                self.pos -= 1
            ids = [(x, db[x].time_created) for x in db.keys()]
            ids.sort(key=lambda x: x[1], reverse=True)
            if len(ids) == 0:
                return None
            self.user: User = db.get(ids[self.pos][0])
            return self.user

