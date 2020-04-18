admin_routine_h_message = 'Привет, admin! ' \
                          'Смотри, сколько людей зарегалось!\n\n' \
                          'Регистраций: {reg_count} \n\n' \
                          '`___________________________________________`\n\n'

MESSAGES = {
    'admin_routine_h_message': admin_routine_h_message,
}


def msg_header_admin(db_size=0):
    return MESSAGES['admin_routine_h_message'].format(reg_count=str(db_size))
