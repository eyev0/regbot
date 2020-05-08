from aiogram import types

from app import dp, Config
from app.db import session_scope
from app.db.models import Enrollment, User, Event
from app.handlers.messages import MESSAGES
from app.handlers.keyboards import events_reply_keyboard
from app.handlers import AdminMenuStates
from app.handlers.util import admin_lambda


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['start'])
async def process_start_command_admin(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    await state.set_state(AdminMenuStates.all()[0])
    with session_scope() as session:
        events_q = session.query(Event) \
            .filter(Event.status < 9) \
            .order_by(Event.edit_datetime.desc())

        events_keyboard = events_reply_keyboard(events_q.all())

        await message.reply(MESSAGES['admin_events'],
                            reply=False,
                            reply_markup=events_keyboard)


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['delete_enroll'])
async def process_delete_enroll_command(message: types.Message):
    args = message.get_args().split(' ')
    if len(args) < 2:
        return
    event_id = args[0]
    uid_to_delete = args[1]
    with session_scope() as session:
        enroll_q = session.query(Enrollment) \
            .join(User) \
            .filter(User.uid == uid_to_delete) \
            .filter(Enrollment.event_id == event_id)
        # get one record
        if enroll_q.count() > 0:
            enroll: Enrollment = enroll_q.all()[0]
            enroll.delete_me(session)
            await message.reply(MESSAGES['admin_record_deleted'],
                                reply=False)


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['delete_user'])
async def process_delete_user_command(message: types.Message):
    uid_to_delete = message.get_args()
    with session_scope() as session:
        user_q = session.query(User) \
            .filter(User.uid == uid_to_delete)
        # get one record
        if user_q.count() > 0:
            user: User = user_q.all()[0]
            user.delete_me(session)
            await message.reply(MESSAGES['admin_record_deleted'],
                                reply=False)


@dp.message_handler(state='*',
                    commands=['admin'])
async def process_admin_command(message: types.Message):
    magic_word = message.get_args()
    uid = message.from_user.id
    if magic_word == 'pls':
        if uid not in Config.admin_ids:
            Config.admin_ids.append(uid)
            await message.reply(MESSAGES['admin_enable'], reply=False)
    elif magic_word == 'no':
        if uid in Config.admin_ids:
            Config.admin_ids.remove(uid)
            await message.reply(MESSAGES['admin_disable'], reply=False)
