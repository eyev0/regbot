import functools
import logging
from collections import Iterable

from app import config

if config.log.add_trace_level_name:
    logging.addLevelName(config.log.trace_level, 'TRACE')


def trace(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        logging.log(config.log.trace_level,
                    f'TRACE: calling {func.__module__}.{func.__name__}(' +
                    f'{",".join([str(x) for x in args])}' +
                    ', ' +
                    f'{", ".join([str(x) + "=" + str(kwargs[x]) for x in kwargs])})')
        result = func(*args, **kwargs)

        if result is not None:
            if isinstance(result, Iterable) and not isinstance(result, str):
                result_str = ', '.join([str(x) for x in result])
            else:
                result_str = result
            logging.log(config.log.trace_level,
                        f'TRACE: {func.__module__}.{func.__name__} '
                        f'returned {result_str!r}')
        return result

    return decorator


def trace_async(func):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        logging.log(config.log.trace_level,
                    f'TRACE: calling {func.__module__}.{func.__name__}(' +
                    f'{",".join([str(x) for x in args])}' +
                    ', ' +
                    f'{", ".join([str(x) + "=" + str(kwargs[x]) for x in kwargs])})')
        result = await func(*args, **kwargs)

        if result is not None:
            if isinstance(result, Iterable) and not isinstance(result, str):
                result_str = ', '.join([str(x) for x in result])
            else:
                result_str = result
            logging.log(config.log.trace_level,
                        f'TRACE: {func.__module__}.{func.__name__} '
                        f'returned {result_str!r}')
        return result

    return decorator
