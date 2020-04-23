from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
    mode = HelperMode.snake_case

    STATE_0 = ListItem()
    STATE_1 = ListItem()
    STATE_2 = ListItem()
    STATE_3 = ListItem()
    STATE_4 = ListItem()
    STATE_5 = ListItem()


class UserListIterator(object):
    map = dict()

    def __init__(self,
                 admin_id):
        self.pos = 0
        self.__class__.map[admin_id] = self

    def fetch(self,
              direction,
              list_):
        if direction is not None:
            if direction[:6] != 'rewind':
                self.pos += (1 if direction == 'forward' else -1)
                # wrap around list
                if self.pos > len(list_) - 1:
                    self.pos = 0
                elif self.pos < 0:
                    self.pos = len(list_) - 1
            else:
                self.pos = (len(list_) - 1 if direction[7:] == 'forward' else 0)

        return list_[self.pos]

    @classmethod
    def get_obj(cls, admin_id):
        i = cls.map.get(admin_id)
        if i is None:
            i = UserListIterator(admin_id)
        return i

    def get_pos(self, list_):
        if list_ is None:
            list_ = []
        if self.pos > len(list_) - 1:
            self.pos = len(list_) - 1
        return self.pos
