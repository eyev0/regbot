import os


class Config(object):
    # test
    # TOKEN = '1285790755:AAFTOTGN6e_a-RAAm7w7CqDLokssL94v98c'
    # prod
    TOKEN = '1298712654:AAGhzGDtJMIaO_2RgWjOV7ZV4yj0-fWbPfs'

    # Proxy
    # PROXY_PROTOCOL = 'http'
    PROXY_PROTOCOL = 'socks5'
    PROXY_IP = '37.228.117.196'
    PROXY_PORT = '1080'
    PROXY_URL = PROXY_PROTOCOL + '://' + PROXY_IP + ':' + PROXY_PORT

    # admins
    # admin_ids = [119707338, 296145754]
    admin_ids = [296145754, ]  # Lera

    RANDOM_KITTEN_JPG = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Red_Kitten_01.jpg/' \
                        '320px-Red_Kitten_01.jpg'

    # file config
    db_path = '/db/users.db' if os.path.exists('/db') else '/home/egor/db/regbot/users.db'
    log_path = '/log/regbot.log' if os.path.exists('/log') else '/home/egor/logs/regbot/regbot.log'
    FSMstorage_path = '/FSMstorage/regbot.json' if os.path.exists('/FSMstorage') else \
        '/home/egor/FSMstorage/regbot.json'
