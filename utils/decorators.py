import asyncio
from functools import partial, wraps
from logging import getLogger

logger = getLogger(__name__)

def multi_try(func=None, *, max_retries: int = 5, retries: int = 0, error='') -> callable:
    if func is None:
        return partial(multi_try, max_retries=max_retries, retries=retries, error=error)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        nonlocal retries
        if max_retries == retries:
            retries = 0
            await func(*args, **kwargs)
        try:
            retries += 1
            res = await func(*args, **kwargs)
            if error != '' and res == error:
                raise TypeError('Invalid return type')
            return res
        except Exception as err:
            logger.error(f'Error in {func.__name__}: {err}')
            await asyncio.sleep(retries)
            await wrapper(*args, **kwargs)
    return wrapper
