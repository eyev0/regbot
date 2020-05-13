greet_new_user = '*Привет!*\n' \
                 'Я - *Лера Трифонова*, а как вас зовут? Напишите, пожалуйста, *фамилию и имя* :)'
pleased_to_meet_you = '*Очень приятно* :)'
show_event_menu = 'Выберите мероприятие'
invoice_prompt = 'А теперь пришлите файл или фото с чеком об оплате.'
registration_complete = '*Спасибо! Вы успешно зарегистрировались :)* \n\n'

registration_exists = '*Вы уже регистрировались на это мероприятие ранее :)*'
no_current_events = 'Больше нет предстоящих мероприятий, на которые вы не зарегистрировались. ' \
                    'Но мы обязательно оповестим вас, когда будет следующий интересный набор! :)'
help_message = 'Это - *бот-помощник* для регистрации на онлайн-классы *Леры* *Трифоновой*\n' \
               'Введи /start, чтобы посмотреть список доступных мероприятий.\n' \
               'Если у тебя есть вопрос про мероприятия или про этого бота - напиши мне *@danceleradance*'

admin_enable = 'Ладно... будешь за админа теперь!'
admin_disable = 'Теперь ты как все, друг!'
admin_events = 'Список активных мероприятий:'
admin_archive = 'Архив мероприятий:'
admin_event_submenu = 'Что будем делать?'
admin_event_not_found = 'Нет такого..'
admin_restart = "Привет, админ! Введи /start, чтобы начать."
admin_record_deleted = 'Запись удалена!'

create_event_prompt_data_1 = 'Название мероприятия'
create_event_prompt_data_2 = 'Короткое описание мероприятия (или минус чтобы пропустить)'
create_event_prompt_data_3 = 'Отлично! Теперь напиши сообщение пользователю ' \
                             'об успешном завершении регистрации(не забудь вставить ссылку на канал)'
create_event_done = 'Готово!'
create_event_oops = 'Ой.'

change_status_prompt = 'Выбери статус'

help_None = 'Привет! Для начала, напиши мне /start :)'
help_state_1 = 'Напишите мне, пожалуйста, свою фамилию и имя :)'
help_state_2 = 'Выберите мероприятие, на которое хотите зарегистрироваться :)'
help_state_3 = 'Осталось прислать квитанцию! Я верю в тебя! :)'

MESSAGES = {
    # user messages
    'greet_new_user': greet_new_user,
    'pleased_to_meet_you': pleased_to_meet_you,
    'show_event_menu': show_event_menu,
    'invoice_prompt': invoice_prompt,
    'registration_complete': registration_complete,

    'registration_exists': registration_exists,
    'no_current_events': no_current_events,
    'help_message': help_message,

    # admin messages
    'admin_enable': admin_enable,
    'admin_disable': admin_disable,
    'admin_events': admin_events,
    'admin_archive': admin_archive,
    'admin_event_submenu': admin_event_submenu,
    'admin_event_not_found': admin_event_not_found,
    'admin_restart': admin_restart,
    'admin_record_deleted': admin_record_deleted,

    # create event messages
    'create_event_prompt_data_1': create_event_prompt_data_1,
    'create_event_prompt_data_2': create_event_prompt_data_2,
    'create_event_prompt_data_3': create_event_prompt_data_3,
    'create_event_done': create_event_done,
    'create_event_oops': create_event_oops,

    # change status messages
    'change_status_prompt': change_status_prompt,

    # help messages by state
    'help_None': help_None,
    'help_state_1': help_state_1,
    'help_state_2': help_state_2,
    'help_state_3': help_state_3,

}


def build_header(event_title: str,
                 event_id: int,
                 all_users_count: int,
                 all_names: list):
    # build Header message
    m_h = f'Ивент: {event_title}\n' \
          f'ID ивента: {event_id}\n' \
          f'Регистраций: {str(all_users_count)} \n' \
          f'Список:\n' + \
          '_______________________\n' + \
          '\n'.join(all_names) + '\n'
    return m_h


def build_caption(uid,
                  username,
                  name_surname,
                  complete,
                  edit_datetime):
    m_b = f'id: {uid}' + (f', @{username}\n' if username is not None else '\n') + \
          f'ФИО: {name_surname}\n' + \
          'Зареган: ' + ('да' if complete else 'нет') + '\n' + \
          f'Когда: {edit_datetime}'
    return m_b
