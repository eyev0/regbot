import sys
import aiogram
from aiogram.bot.api import *


async def make_request_custom(session, token, method, data=None, files=None, **kwargs):
    # log.debug(f"Make request: '{method}' with data: {data} and files {files}")
    log.debug('Make request: "%s" with data: "%r" and files "%r"', method, data, files)

    url = Methods.api_url(token=token, method=method)

    req = compose_data(data, files)
    try:
        async with session.post(url, data=req, **kwargs) as response:
            return check_result(method, response.content_type, response.status, await response.text())
    except aiohttp.ClientProxyConnectionError as e:
        log.error(f'{e.__class__.__name__}: {e}')
        raise exceptions.NetworkError(f"aiohttp client throws an error: {e.__class__.__name__}: {e}")
    except aiohttp.ClientError as e:
        raise exceptions.NetworkError(f"aiohttp client throws an error: {e.__class__.__name__}: {e}")


sys.modules['aiogram'].bot.api.make_request = make_request_custom
