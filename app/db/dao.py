import sqlalchemy.orm

from app.db.models import User
from app.utils import WrappingListIterator


class UserDAO(User):
    @classmethod
    def get_by_uid(cls, session: sqlalchemy.orm.Session, uid):
        user_q = session.query(cls) \
            .filter_by(user_id=uid)
        if user_q.count() > 0:
            return user_q.all()[0]
        else:
            return None

    @classmethod
    def get_all_list(cls, session: sqlalchemy.orm.Session):
        all_users_q = session.query(User) \
            .order_by(User.edit_datetime.desc())
        if all_users_q.count() > 0:
            return all_users_q.all()
        else:
            return None

    @classmethod
    def get_new_list(cls, session: sqlalchemy.orm.Session):
        new_users_q = session.query(User) \
            .order_by(User.edit_datetime.desc())
        if new_users_q.count() > 0:
            return new_users_q.all()
        else:
            return None

    @classmethod
    def fetch(cls, session: sqlalchemy.orm.Session, direction):
        list_ = cls.get_all_list(session)
        if list_ is not None:
            return WrappingListIterator.get_obj().fetch(list_, direction)
        return None