from utils import User


def msg_header_admin(db_size=0):
    return 'Привет, admin! \n\n' \
           f'Регистраций: {str(db_size)} \n\n' \
           '`_______________________`\n\n'


def msg_body_admin(user: User):
    return f'id: {user.user_id}\n' \
           f'username: @{user.username}\n' \
           f'Фамилия и имя: {user.name_surname}\n' \
           f'Дата регистрации: {user.time_created}'
