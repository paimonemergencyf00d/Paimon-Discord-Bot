import asyncio
import datetime
from typing import Callable

import aiohttp
import genshin
import sentry_sdk

from database import Database, User
from utility import LOG, config

from .errors import GenshinAPIException, UserDataNotFound


def generalErrorHandler(func: Callable):
    """Generic exception handling decorator for using genshin.py functions"""

    async def wrapper(*args, **kwargs):
        user_id = -1
        # Find the user_id from the function parameters
        for arg in args:
            if isinstance(arg, int) and len(str(arg)) >= 15:
                user_id = arg
                break
        try:
            # Add a retry mechanism for specific errors
            RETRY_MAX = 3
            for retry in range(RETRY_MAX, -1, -1):
                try:
                    result = await func(*args, **kwargs)

                    # If the command is successfully used, the user's last usage time will be updated.
                    user = await Database.select_one(User, User.discord_id.is_(user_id))
                    if user is not None:
                        user.last_used_time = datetime.datetime.now()
                        await Database.insert_or_replace(user)

                    return result
                except (genshin.errors.InternalDatabaseError, aiohttp.ClientOSError) as e:
                    LOG.FuncExceptionLog(user_id, f"{func.__name__} (retry={retry})", e)
                    if retry == 0:  # Throws an exception when the number of retries is exhausted
                        raise
                    else:
                        # Add a waiting time between retries and increment the waiting time each time
                        await asyncio.sleep(1.0 + RETRY_MAX - retry)
                        continue
        except genshin.errors.DataNotPublic as e:
            LOG.FuncExceptionLog(user_id, func.__name__, e)
            raise GenshinAPIException(e, "This feature is not enabled. Please enable it from the Personal Records->Settings on the Hoyolab website or App.")
        except genshin.errors.InvalidCookies as e:
            LOG.FuncExceptionLog(user_id, func.__name__, e)
            raise GenshinAPIException(e, "The cookie has expired. Please get a new cookie from Hoyolab.")
        except genshin.errors.GeetestError as e:
            LOG.FuncExceptionLog(user_id, func.__name__, e)
            url = f"{config.geetest_solver_url}/geetest/starrail_battlechronicle/{user_id}"
            raise GenshinAPIException(e, f"To trigger Hoyolab graphic verification, please [>>click this link<<]({url}/) to go to the web page for manual unlock.")
        except genshin.errors.RedemptionException as e:
            LOG.FuncExceptionLog(user_id, func.__name__, e)
            raise GenshinAPIException(e, e.original)
        except genshin.errors.GenshinException as e:
            LOG.FuncExceptionLog(user_id, func.__name__, e)
            sentry_sdk.capture_exception(e)
            raise GenshinAPIException(e, e.original)
        except UserDataNotFound as e:
            LOG.FuncExceptionLog(user_id, func.__name__, e)
            raise Exception(str(e))
        except Exception as e:
            LOG.FuncExceptionLog(user_id, func.__name__, e)
            sentry_sdk.capture_exception(e)
            raise

    return wrapper
