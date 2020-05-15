import json


class Config(object):

    def __init__(self, container, test_env):
        self.container = container
        self.test_env = test_env

        if self.container:
            self.vol_path = '/vol'
        else:
            self.vol_path = '/home/egor/regbot'
            if self.test_env:
                self.vol_path = self.vol_path + '/test'

        self.config_path = self.vol_path + '/config.json'
        self.proxy_path = self.vol_path + '/proxy.json'
        self.db_path = self.vol_path + '/users.db'
        self.log_path = self.vol_path + '/regbot.log'
        self.FSMstorage_path = self.vol_path + '/FSMstorage.json'
        self.navigation_storage = self.vol_path + '/navigation_storage.json'

        with open(self.config_path, 'rb') as f:
            self.conf = json.load(f)
            self.TOKEN = self.conf['TOKEN']
            self.admin_ids = self.conf['admin_ids']

        with open(self.proxy_path, 'rb') as f:
            self.proxy_conf = json.load(f)
            self.PROXY_PROTOCOL = self.proxy_conf['protocol']
            self.PROXY_IP = self.proxy_conf['ip']
            self.PROXY_PORT = self.proxy_conf['port']
            self.PROXY_URL = self.PROXY_PROTOCOL + '://' + self.PROXY_IP + ':' + self.PROXY_PORT

    def __repr__(self):
        return f'Config(container={self.container}, test_env={self.test_env}, TOKEN={self.TOKEN}, ' \
               f'PROXY_URL={self.PROXY_URL}, vol_dir={self.vol_path}, admin_ids={self.admin_ids})'
