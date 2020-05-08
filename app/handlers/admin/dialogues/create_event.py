from aiogram import types
from aiogram.types import ContentType

from app import dp
from app.db import session_scope
from app.db.models import Event
from app.handlers import CreateEventStates
from app.handlers.messages import MESSAGES
from app.handlers.util import admin_lambda


@dp.message_handler(admin_lambda(),
                    state='*',
                    commands=['create_event'])
async def process_create_event_command(message: types.Message):
    uid = message.from_user.id
    state = dp.current_state(user=uid)
    await message.reply(MESSAGES['create_event_prompt_name'],
                        reply=False)
    await state.set_state(CreateEventStates.all()[1])


@dp.message_handler(state=CreateEventStates.CREATE_EVENT_STATE_1 | CreateEventStates.CREATE_EVENT_STATE_2 | CreateEventStates.CREATE_EVENT_STATE_3,
                    content_types=ContentType.TEXT)
async def process_create_event_data(message: types.Message):
    uid = message.from_user.id
    input_data = message.text if message.text != '-' else ''
    state = dp.current_state(user=uid)
    state_number = int(str(await state.get_state())[-1:])
    state_data = await state.get_data() or {}
    state_data[state_number] = input_data
    await state.set_data(state_data)
    if state_number < 3:
        state_number += 1
        await state.set_state(CreateEventStates.all()[state_number])
        await message.reply(MESSAGES['create_event_prompt_data_' + str(state_number)],
                            reply=False)
    else:

        with session_scope() as session:
            Event(title=state_data[1],
                  description=state_data[2],
                  access_info=state_data[3]) \
                .insert_me(session)
        await message.reply(MESSAGES['create_event_done'],
                            reply=False)
        await state.set_state(None)
        await state.set_data(None)


@dp.message_handler(state=CreateEventStates.all())
async def process_event_access_info(message: types.Message):
    await message.reply(MESSAGES['create_event_oops'],
                        reply=False)
