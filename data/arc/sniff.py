import shelve

from app.db import *
from app.db.models import User

with shelve.open('./data/f') as db:
    ids = [(x, db[x]) for x in db]
    print(ids)
    with session_scope() as session:
        for uid, x in ids:
            user = User(uid, x.username,
                        x.name_surname, x.reg_passed, False,
                        x.payment.file_type if x.payment is not None else '',
                        x.payment.file_id if x.payment is not None else '')
            session.add(user)
            session.commit()
        print(session.query(User).all())
