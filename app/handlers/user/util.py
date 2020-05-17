from aiogram import types
from sqlalchemy import and_, or_

from app import dp, bot
from app.db import session_scope
from app.db.models import Event, User, Enrollment
from app.handlers.keyboards import events_reply_keyboard
from app.handlers.messages import MESSAGES
from app.handlers.states import UserStates


async def show_event_list_task(uid,
                               markup_only=False):
    state = dp.current_state(user=uid)
    with session_scope() as session:
        events_q = session.query(Event) \
            .join(User, User.uid == uid) \
            .outerjoin(Enrollment, and_(Enrollment.user_id == User.id, Enrollment.event_id == Event.id)) \
            .filter(Event.status == 1) \
            .filter(or_(Enrollment.id == None, Enrollment.complete == False)) \
            .order_by(Event.edit_datetime.desc())

        if events_q.count() > 0:
            m_text = MESSAGES['show_event_menu']
            events_keyboard = events_reply_keyboard(events_q.all())
            if markup_only:
                return events_keyboard
            else:
                await bot.send_message(uid,
                                       text=m_text,
                                       reply_markup=events_keyboard)
                await state.set_state(UserStates.all()[2])
        else:
            m_text = MESSAGES['no_current_events']
            await bot.send_message(uid,
                                   text=m_text)

        return None
