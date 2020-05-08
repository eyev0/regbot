class WrappingListIterator(object):

    obj = None

    def __init__(self):
        self.pos = 0
        self.__class__.obj = self

    @classmethod
    def get_obj(cls):
        if cls.obj is None:
            cls.obj = cls()
        return cls.obj

    def fetch(self, list_, direction=None):
        if len(list_) == 0:
            return None
        if direction is not None:
            if direction[:6] != 'rewind':
                self.pos += (1 if direction == 'forward' else -1)
            else:
                self.pos = (len(list_) - 1 if direction[7:] == 'forward' else 0)
        # wrap around list
        if self.pos > len(list_) - 1:
            self.pos = 0
        elif self.pos < 0:
            self.pos = len(list_) - 1

        return list_[self.pos]
