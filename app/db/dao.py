import sqlalchemy.orm

from app.db.models import User, Enrollment, Event
from app.utils import WrappingListIterator


class UserDAO(User):
    @classmethod
    def get_by_uid(cls, session: sqlalchemy.orm.Session, uid):
        user_q = session.query(cls) \
            .filter_by(uid=uid)
        if user_q.count() > 0:
            return user_q.all()[0]
        else:
            return None

    @classmethod
    def get_all_query(cls, session: sqlalchemy.orm.Session):
        return session.query(User) \
            .order_by(User.edit_datetime.desc())

    @classmethod
    def get_all_list(cls, session: sqlalchemy.orm.Session):
        all_users_q = cls.get_all_query(session)
        if all_users_q.count() > 0:
            return all_users_q.all()
        else:
            return []

    @classmethod
    def get_new_list(cls, session: sqlalchemy.orm.Session):
        new_users_q = session.query(User) \
            .order_by(User.edit_datetime.desc())
        if new_users_q.count() > 0:
            return new_users_q.all()
        else:
            return []

    @classmethod
    def fetch(cls, session: sqlalchemy.orm.Session, direction):
        list_ = cls.get_all_list(session)
        if len(list_) > 0:
            return WrappingListIterator.get_obj().fetch(list_, direction)
        return None


class EnrollmentDAO(Enrollment):

    @classmethod
    def get_by_uid_event_id(cls, session: sqlalchemy.orm.Session, uid: int, event_id: int):
        enrollment_by_user_event_q = session.query(Enrollment) \
            .join(User, Enrollment.user_id == User.id) \
            .join(Event, Enrollment.event_id == Event.id) \
            .filter(User.uid == uid) \
            .filter(Event.id == event_id)
        if enrollment_by_user_event_q.count() > 0:
            return enrollment_by_user_event_q.all()[0]
        else:
            return None

    @classmethod
    def get_event_enrollments(cls, session: sqlalchemy.orm.Session, event_id: int):
        event_enrollments_q = session.query(Enrollment) \
            .join(Event, Enrollment.event_id == Event.id) \
            .filter(Event.id == event_id)
        if event_enrollments_q.count() > 0:
            return event_enrollments_q.all()
        else:
            return None

    @classmethod
    def fetch(cls, session: sqlalchemy.orm.Session, direction):
        list_ = cls.get_all_list(session)
        if len(list_) > 0:
            return WrappingListIterator.get_obj().fetch(list_, direction)
        return None


class EventDAO(Event):

    @classmethod
    def get_by_event_id(cls, session: sqlalchemy.orm.Session, event_id: int):
        event_q = session.query(Event) \
            .filter(Event.id == event_id)
        if event_q.count() > 0:
            return event_q.all()[0]
        else:
            return None
