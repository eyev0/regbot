import logging
from contextlib import contextmanager

import sqlalchemy.orm

from app.db import Session
from app.db.models import User, Enrollment, Event


@contextmanager
def user_enrollment_by_event_id(event_id):
    session: sqlalchemy.orm.Session = Session()
    try:
        query = session.query(User, Enrollment) \
            .join(Enrollment) \
            .filter(Enrollment.event_id == event_id) \
            .order_by(Enrollment.edit_datetime.desc())
        yield query
        session.commit()
    except Exception as e:
        logging.error(f'Got Error From Database:{e}')
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def user_by_uid(uid):
    session: sqlalchemy.orm.Session = Session()
    try:
        query = session.query(User) \
            .filter(User.uid == uid)
        yield query
        session.commit()
    except Exception as e:
        logging.error(f'Got Error From Database:{e}')
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def enrollment_by_event_id_uid(event_id, uid):
    session: sqlalchemy.orm.Session = Session()
    try:
        query = session.query(Enrollment) \
            .join(User) \
            .filter(Enrollment.event_id == event_id) \
            .filter(User.uid == uid)
        yield query
        session.commit()
    except Exception as e:
        logging.error(f'Got Error From Database:{e}')
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def user_enrollment_event_by_event_id_uid(event_id, uid):
    session: sqlalchemy.orm.Session = Session()
    try:
        subquery_event = session.query(Event) \
            .filter(Event.id == event_id) \
            .with_labels() \
            .subquery('subquery_event')

        subquery_enrollment_user = session.query(Enrollment, User) \
            .join(User) \
            .filter(User.uid == uid) \
            .with_labels() \
            .subquery('subquery_enrollment_user')

        query = session.query(subquery_event, subquery_enrollment_user) \
            .outerjoin(subquery_enrollment_user,
                       subquery_event.c.event_id == subquery_enrollment_user.c.enrollment_event_id)

        yield query
        session.commit()
    except Exception as e:
        logging.error(f'Got Error From Database:{e}')
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def event_by_event_id(event_id):
    session: sqlalchemy.orm.Session = Session()
    try:
        query = session.query(Event) \
            .filter(Event.id == event_id)
        yield query
        session.commit()
    except Exception as e:
        logging.error(f'Got Error From Database:{e}')
        session.rollback()
        raise
    finally:
        session.close()
