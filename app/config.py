import json
import os


class Config(object):
    # test
    # TOKEN = '1285790755:AAFTOTGN6e_a-RAAm7w7CqDLokssL94v98c'
    # prod
    TOKEN = '1298712654:AAGhzGDtJMIaO_2RgWjOV7ZV4yj0-fWbPfs'

    # Proxy
    # PROXY_PROTOCOL = 'http'
    # PROXY_PROTOCOL = 'socks5'
    # PROXY_IP = '217.61.109.129'
    # PROXY_PORT = '8080'
    # PROXY_URL = PROXY_PROTOCOL + '://' + PROXY_IP + ':' + PROXY_PORT

    # admins
    # admin_ids = [119707338, 296145754]
    admin_ids = [296145754, ]  # Lera

    RANDOM_KITTEN_JPG = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Red_Kitten_01.jpg/' \
                        '320px-Red_Kitten_01.jpg'

    # file config
    vol_dir = '/vol' if os.path.exists('/vol') else '/home/egor/regbot'
    proxy_path = vol_dir + '/proxy.json'
    db_path = vol_dir + '/users.db'
    log_path = vol_dir + '/regbot.log'
    FSMstorage_path = vol_dir + '/FSMstorage.json'

    proxy_conf = json.load(open(proxy_path, 'rb'))
    PROXY_PROTOCOL = proxy_conf['protocol']
    PROXY_IP = proxy_conf['ip']
    PROXY_PORT = proxy_conf['port']
    PROXY_URL = PROXY_PROTOCOL + '://' + PROXY_IP + ':' + PROXY_PORT
