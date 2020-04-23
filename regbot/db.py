import logging
from contextlib import contextmanager
from datetime import datetime

import pytz
import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from regbot.config import Config

clock = datetime(2020, 1, 1, tzinfo=pytz.timezone('Europe/Moscow'))

engine = sqlalchemy.create_engine(f'sqlite:///{Config.db_filename}')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String(255))
    name_surname = Column(String(255))
    is_registered = Column(Boolean(), default=False)
    admin_check = Column(Boolean(), default=False)
    file_type = Column(String(10))
    file_id = Column(String(1000))
    edit_datetime = Column(DateTime, default=clock.now())

    def __init__(self,
                 user_id,
                 username='',
                 name_surname='',
                 registered=False,
                 admin_check=False,
                 file_type='document',
                 file_id='',
                 edit_datetime=clock.now()):
        self.user_id = user_id
        self.username = username
        self.name_surname = name_surname
        self.is_registered = registered
        self.admin_check = admin_check
        self.file_type = file_type
        self.file_id = file_id
        self.edit_datetime = edit_datetime

    def __repr__(self):
        return "User(id={}, user_id={}, username={}, name_surname={}, registered={}, " \
               "admin_check={}, file_type={}, file_id={}, edit_datetime={})"\
            .format(self.id, self.user_id, self.username, self.name_surname, self. is_registered,
                    self.admin_check, self.file_type, self.file_id, self.edit_datetime)


def create_user(session: sqlalchemy.orm.Session, u_id):
    u = User(u_id)
    session.add(u)
    session.commit()
    return


Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


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
