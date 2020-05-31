import functools
import logging
from contextlib import contextmanager

import sqlalchemy.orm

from app.db import Session


class Direction(object):
    REWIND_BACK = '<<'
    REWIND_FORWARD = '>>'
    BACK = ['<', '-']
    FORWARD = ['>', '+']
    map = {

    }

    @staticmethod
    def is_rewind(data):
        return len(data) > 1

    def __init__(self, data: str):
        self.direction = data
        self.rewind = self.is_rewind(data)
        self.back = data[-1:] in self.BACK
        self.forward = data[-1:] in self.FORWARD


def fetch_list(list_: list,
               current_pos: int,
               do_scroll=False,
               where: str = None):
    if len(list_) == 0:
        return None
    if do_scroll:
        direction = Direction(where)
        if direction.rewind:
            current_pos = (len(list_) - 1 if direction.forward else 0)
        else:
            current_pos += (1 if direction.forward else -1)
    # wrap around list
    if current_pos > len(list_) - 1:
        current_pos = 0
    elif current_pos < 0:
        current_pos = len(list_) - 1

    return list_[current_pos], current_pos


class WrappingListIterator(object):
    pass


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session: sqlalchemy.orm.Session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logging.error(f'Got Error From Database:{e}')
        session.rollback()
        raise
    finally:
        session.close()


def use_db_session(func):
    """Add session keyword arg to this function call"""

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        with session_scope() as session:
            kwargs['session'] = session
            return func(*args, **kwargs)

    return decorator


def sql_result(query: sqlalchemy.orm.Query):
    """Return rowcount, first row and rows list for query"""
    rowcount = query.count()
    if rowcount > 0:
        rows_list = query.all()
        first_row = rows_list[0]
    else:
        rows_list = first_row = None

    return rowcount, first_row, rows_list
