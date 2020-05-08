from aiogram import types
from sqlalchemy import and_, or_

from app import dp
from app.db import session_scope
from app.db.models import Event, User, Enrollment
from app.handlers.messages import MESSAGES
from app.handlers.keyboards import events_reply_keyboard
from app.handlers import UserStates


async def show_event_list_task(message: types.Message):
    uid = message.from_user.id
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
            await state.set_state(UserStates.all()[2])
        else:
            m_text = MESSAGES['no_current_events']
            events_keyboard = None

        await message.reply(m_text,
                            reply=False,
                            reply_markup=events_keyboard)