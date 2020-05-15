class Direction(object):
    REWIND_BACK = '<<'
    REWIND_FORWARD = '>>'
    BACK = ['<', '-']
    FORWARD = ['>', '+']
    map = {

    }

    @staticmethod
    def is_rewind(data):
        return len(data) > 1

    def __init__(self, data: str):
        self.direction = data
        self.rewind = self.is_rewind(data)
        self.back = data[-1:] in self.BACK
        self.forward = data[-1:] in self.FORWARD


def fetch_list(list_: list,
               current_pos: int,
               do_scroll=False,
               where: str = None):
    if len(list_) == 0:
        return None
    if do_scroll:
        direction = Direction(where)
        if direction.rewind:
            current_pos = (len(list_) - 1 if direction.forward else 0)
        else:
            current_pos += (1 if direction.forward else -1)
    # wrap around list
    if current_pos > len(list_) - 1:
        current_pos = 0
    elif current_pos < 0:
        current_pos = len(list_) - 1

    return list_[current_pos], current_pos


class WrappingListIterator(object):
    pass
