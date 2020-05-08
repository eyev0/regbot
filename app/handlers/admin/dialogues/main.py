from aiogram import types
from aiogram.utils.exceptions import BadRequest

from app import dp, bot
from app.db import session_scope
from app.db.models import Enrollment, User, Event
from app.db.util import WrappingListIterator
from app.handlers import AdminMenuStates
from app.handlers.admin import kitty
from app.handlers.keyboards import keyboard_refresh, keyboard_scroll, send_remove_reply_keyboard
from app.handlers.messages import build_header, build_caption, MESSAGES


@dp.message_handler(state=AdminMenuStates.ADMIN_MENU_STATE_0)
async def process_event_click_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)

    with session_scope() as session:
        event_q = session.query(Event) \
            .filter(Event.title == message.text)
        if event_q.count() == 0:
            await message.reply(MESSAGES['admin_event_not_found'],
                                reply=False)
            return
        else:
            await send_remove_reply_keyboard(message)
        event: Event = event_q.all()[0]
        data = {'event_id': event.id}
        await state.set_data(data)

        users_enrolls_q = session.query(User, Enrollment) \
            .join(Enrollment) \
            .join(Event) \
            .filter(Event.id == data['event_id']) \
            .order_by(Enrollment.edit_datetime.desc())
        # get all user and enrollment data
        users_enrolls_list, count = users_enrolls_q.all(), users_enrolls_q.count()
        all_names = [x[0].name_surname for x in users_enrolls_list]

        # header message
        m_h = build_header(event.title,
                           event.id,
                           count,
                           count,
                           all_names)
        # send header
        await message.reply(m_h,
                            reply=False,
                            reply_markup=keyboard_refresh)

        if count == 0:
            return

        # get one record
        user, enrollment = WrappingListIterator.get_obj().fetch(users_enrolls_list)

        # body message
        m_b = build_caption(user.uid,
                            user.username,
                            user.name_surname,
                            enrollment.complete,
                            enrollment.edit_datetime)
        # send body
        if enrollment.complete:
            try:
                if enrollment.file_type == 'photo':
                    await bot.send_photo(message.chat.id,
                                         photo=enrollment.file_id,
                                         caption=m_b,
                                         reply_markup=keyboard_scroll)
                else:
                    await bot.send_document(message.chat.id,
                                            document=enrollment.file_id,
                                            caption=m_b,
                                            reply_markup=keyboard_scroll)
            except BadRequest:
                # can't send media
                await bot.send_document(message.chat.id,
                                        document=kitty,
                                        caption=m_b,
                                        reply_markup=keyboard_scroll)
        else:
            await bot.send_document(message.chat.id,
                                    document=kitty,
                                    caption=m_b,
                                    reply_markup=keyboard_scroll)
