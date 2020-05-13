class Direction(object):
    REWIND_BACK = '<<'
    REWIND_FORWARD = '>>'
    BACK = '<'
    FORWARD = '>'
    map = {

    }

    @staticmethod
    def is_rewind(data):
        return len(data) > 1

    def __init__(self, data: str):
        self.direction = data
        self.rewind = self.is_rewind(data)
        self.back = data[-1:] == self.BACK
        self.forward = data[-1:] == self.FORWARD


class WrappingListIterator(object):

    def __init__(self):
        self.pos = 0

    def fetch(self, list_: list, do_scroll=False, where: str = None):
        if len(list_) == 0:
            return None
        if do_scroll:
            direction = Direction(where)
            if direction.rewind:
                self.pos = (len(list_) - 1 if direction.forward else 0)
            else:
                self.pos += (1 if direction.forward else -1)
        # wrap around list
        if self.pos > len(list_) - 1:
            self.pos = 0
        elif self.pos < 0:
            self.pos = len(list_) - 1

        return list_[self.pos]
