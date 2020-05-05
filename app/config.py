import os


class Config(object):
    # test
    # TOKEN = '1285790755:AAFTOTGN6e_a-RAAm7w7CqDLokssL94v98c'
    # prod
    TOKEN = '1298712654:AAGhzGDtJMIaO_2RgWjOV7ZV4yj0-fWbPfs'

    # PROXY_PROTOCOL = 'socks5'
    # PROXY_IP = '91.225.165.134'
    # PROXY_PORT = '8888'

    PROXY_PROTOCOL = 'socks5'
    # PROXY_PROTOCOL = 'http'
    PROXY_IP = '148.251.234.93'
    PROXY_PORT = '1080'
    PROXY_URL = PROXY_PROTOCOL + '://' + PROXY_IP + ':' + PROXY_PORT

    admin_ids = [119707338, 296145754]
    # admin_ids = [x + 1 for x in admin_ids]

    RANDOM_KITTEN_JPG = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Red_Kitten_01.jpg/' \
                        '320px-Red_Kitten_01.jpg'

    # webhook settings
    WEBHOOK_HOST = 'https://cryptic-scrubland-09137.herokuapp.com/'
    WEBHOOK_URL = f"{WEBHOOK_HOST}{TOKEN}"

    # webserver settings
    WEBAPP_HOST = '0.0.0.0'  # or ip
    try:
        WEBAPP_PORT = int(os.environ.get('PORT', 8443))
    except ValueError:
        WEBAPP_PORT = 8443

    # db_filename = '/home/db/users.db'
    db_filename = '/db/users.db' if os.path.exists('/db') else '/home/egor/db/regbot/users.db'
