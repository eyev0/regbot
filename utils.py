from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
    mode = HelperMode.snake_case

    STATE_0 = ListItem()
    STATE_1 = ListItem()
    STATE_2 = ListItem()
    STATE_3 = ListItem()
    STATE_4 = ListItem()
    STATE_5 = ListItem()


class User(object):

    def __init__(self,
                 user_id,
                 username,
                 payment_type,
                 payment_info):
        self.user_id = user_id
        self.username = username
        self.payment_type = payment_type
        self.payment_info = payment_info
