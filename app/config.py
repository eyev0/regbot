import json

import aiohttp
from aiogram.contrib.fsm_storage.redis import RedisStorage2

APP_NAME = 'regbot'


class Config(object):

    def __init__(self, container, test_env, webhook_mode, proxy):
        self.container = container
        self.test_env = test_env
        self.webhook_mode = webhook_mode
        self.use_proxy = proxy

        if self.container:
            self.vol_path = '/vol'
        else:
            self.vol_path = f'/home/egor/{APP_NAME}'

        self.config_json = self.vol_path + '/config.json'
        self.proxy_json = self.vol_path + '/proxy.json'
        self.log_path = self.vol_path + f'/{APP_NAME}{"-test" if test_env else ""}.log'

        self.db_dialect = 'postgres'
        self.db_user = 'docker'
        self.db_password = 'docker'
        self.db_name = 'docker'
        if self.container:
            self.db_host = 'db'
            self.redis_host = 'redis'
            self.db_port = '5432'
            self.redis_port = '6379'
        else:
            self.db_host = self.redis_host = 'localhost'
            self.db_port = '15432'
            self.redis_port = '16379'

        self.db_connect_string = self.db_dialect + '://' + self.db_user + ':' + self.db_password + '@' \
                                 + self.db_host + ':' + self.db_port + '/' + self.db_name

        if test_env:
            prefix = 'test'
        else:
            prefix = ''
        self.states_storage = RedisStorage2(host=self.redis_host,
                                            port=self.redis_port,
                                            db=0,
                                            prefix=prefix + 'fsm')
        self.navigation_storage = RedisStorage2(host=self.redis_host,
                                                port=self.redis_port,
                                                db=0,
                                                prefix=prefix + 'nav')
        self.notification_storage = RedisStorage2(host=self.redis_host,
                                                  port=self.redis_port,
                                                  db=0,
                                                  prefix=prefix + 'notify')

        with open(self.config_json, 'rb') as f:
            self.conf = json.load(f)
            self.TOKEN = self.conf['TOKEN' if not test_env else 'TOKEN_TEST']
            self.check_admin = self.conf['check_admin']
            self.admins = []

        if self.use_proxy:
            with open(self.proxy_json, 'rb') as f:
                self.proxy_conf = json.load(f)
                self.PROXY_PROTOCOL = self.proxy_conf['protocol']
                self.PROXY_IP = self.proxy_conf['ip']
                self.PROXY_PORT = self.proxy_conf['port']
                self.PROXY_USERNAME = self.proxy_conf['username'] or ''
                self.PROXY_PASSWD = self.proxy_conf['password'] or ''
                self.PROXY_URL = self.PROXY_PROTOCOL + '://' + self.PROXY_IP + ':' + self.PROXY_PORT

                if len(self.PROXY_USERNAME) > 0:
                    self.PROXY_AUTH = aiohttp.BasicAuth(login=self.PROXY_USERNAME, password=self.PROXY_PASSWD)
                else:
                    self.PROXY_AUTH = None
        else:
            self.PROXY_URL = None
            self.PROXY_AUTH = None

    def __repr__(self):
        return f'Config(container={self.container}, test_env={self.test_env}, TOKEN={self.TOKEN}, ' \
               f'PROXY_URL={self.PROXY_URL}, check_admin={self.check_admin})'
