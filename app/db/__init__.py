import logging
from contextlib import contextmanager

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.orm import scoped_session, sessionmaker

from app import config
from app.db.models import Base

engine = sqlalchemy.create_engine(f'sqlite:///{config.db_path}')

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


from .util import *

enrolls_row_iterator = WrappingListIterator()
status_row_iterator = WrappingListIterator()
