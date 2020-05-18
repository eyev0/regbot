import logging


def log_call(func):
    def decorator(*args, **kwargs):
        logging.warning(func.__name__ + '(' + ', '.join([str(x) for x in args]) + ', '.join(
            [str(x) + '=' + str(kwargs[x]) for x in kwargs]))
        return func(*args, **kwargs)

    return decorator
