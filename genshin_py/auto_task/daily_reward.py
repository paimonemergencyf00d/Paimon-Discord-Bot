import asyncio
from datetime import datetime
from typing import Any, ClassVar, Final

import aiohttp
import discord
import sentry_sdk
from discord.ext import commands

import database
from database import Database, GeetestChallenge, ScheduleDailyCheckin, User
from utility import LOG, EmbedTemplate, config

from .. import claim_daily_reward


class DailyReward:
    """Types of automatic scheduling

    Methods
    -----
    execute(bot: `commands.Bot`)
        Execute automatic scheduling
    """

    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()
    # 統計簽到人數
    _total: ClassVar[dict[str, int]] = {}
    """The total number of people who signed in dict[host, count]"""
    _honkai_count: ClassVar[dict[str, int]] = {}
    """Number of people who signed in to Honkai Impact 3 dict[host, count]"""
    _starrail_count: ClassVar[dict[str, int]] = {}
    """Number of people who signed in to the Honkai: Star Rail dict[host, count]"""
    _zzz_count: ClassVar[dict[str, int]] = {}
    """Number of people who signed in to the Zenless Zone Zero dict[host, count]"""
    _themis_count: ClassVar[dict[str, int]] = {}
    """Number of people signed in to the undecided event book dict[host, count]"""

    @classmethod
    async def execute(cls, bot: commands.Bot):
        """Execute automatic scheduling, sign in users and count sign-in data

        Parameters
        -----
        bot: `commands.Bot`
            Discord bot client
        """
        if cls._lock.locked():
            return
        await cls._lock.acquire()
        try:
            LOG.System("Daily automatic sign-in starts")

            # 初始化
            queue: asyncio.Queue[ScheduleDailyCheckin] = asyncio.Queue()
            cls._total = {}
            cls._honkai_count = {}
            cls._starrail_count = {}
            cls._zzz_count = {}
            cls._themis_count = {}
            daily_users = await Database.select_all(ScheduleDailyCheckin)

            # Put all users who need to sign in into a queue (Producer)
            for user in daily_users:
                if user.next_checkin_time < datetime.now():
                    await queue.put(user)

            # Create a local sign-in task (Consumer)
            tasks = [asyncio.create_task(cls._claim_daily_reward_task(queue, "LOCAL", bot))]
            # Create a remote sign-in task (Consumer)
            for host in config.daily_reward_api_list:
                tasks.append(asyncio.create_task(cls._claim_daily_reward_task(queue, host, bot)))

            await queue.join()  # Wait for all users to sign in
            for task in tasks:  # Close the sign-in task
                task.cancel()

            _log_message = (
                f"Automatic sign-in ends: Total {sum(cls._total.values())} People sign in,"
                + f"其中 {sum(cls._honkai_count.values())} People sign in to Honkai Impact 3,"
                + f"{sum(cls._starrail_count.values())} People signed in to the Honkai: Star Rail,"
                + f"{sum(cls._zzz_count.values())} People sign in to the Zenless Zone Zero,"
                + f"{sum(cls._themis_count.values())} People sign in to the pending event book\n"
            )
            for host in cls._total.keys():
                _log_message += (
                    f"- {host}：{cls._total.get(host)}、{cls._honkai_count.get(host)}、"
                    + f"{cls._starrail_count.get(host)}、{cls._zzz_count.get(host)}\n"
                )
            LOG.System(_log_message)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            LOG.Error(f"Automatically schedule DailyReward and an error occurred: {e}")
        finally:
            cls._lock.release()

    @classmethod
    async def _claim_daily_reward_task(
        cls, queue: asyncio.Queue[ScheduleDailyCheckin], host: str, bot: commands.Bot
    ):
        """Get the user from the passed asyncio.Queue, then sign in daily and send a message to the user based on the sign-in result

        Parameters
        -----
        queue: `asyncio.Queue[ScheduleDailyCheckin]`
            A queue of users who need to sign in
        host: `str`
           Signed in host
            - Local: Fixed as a string "LOCAL"
            - Remote: Check-in API URL

        bot: `commands.Bot`
            Discord bot client
        """
        LOG.Info(f"Automatically schedule the check-in task to start: {host}")
        if host != "LOCAL":
            # First test whether the API is normal
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(host) as resp:
                        if resp.status != 200:
                            raise Exception(f"Http status code {resp.status}")
                except Exception as e:
                    sentry_sdk.capture_exception(e)
                    LOG.Error(f"Automatically schedule DailyReward test API {host} An error occurred: {e}")
                    return

        cls._total[host] = 0  # Initialize the number of sign-ins
        cls._honkai_count[host] = 0  # Initialize the number of people who signed in to Honkai Impact 3
        cls._starrail_count[host] = 0  # Initialize the number of people who signed in to the Honkai: Star Rail
        cls._zzz_count[host] = 0  # Initialize the number of people who sign in to the Zenless Zone Zero
        cls._themis_count[host] = 0  # Initialize the number of people who signed in to the undecided event book
        MAX_API_ERROR_COUNT: Final[int] = 20  # Maximum number of remote API errors
        api_error_count = 0  # The number of errors that occurred in the remote API

        while True:
            user = await queue.get()
            try:
                message = await cls._claim_daily_reward(host, user)
            except Exception as e:
                await queue.put(user)  # An exception occurred during sign-in, placing the user back in the queue
                api_error_count += 1
                LOG.Error(f"Remote API：{host} An error occurred ({api_error_count}/{MAX_API_ERROR_COUNT})")
                # If the error exceeds MAX_API_ERROR_COUNT times, the sign-in task will be stopped
                if api_error_count >= MAX_API_ERROR_COUNT:
                    sentry_sdk.capture_exception(e)
                    return
            else:
                # After successful sign-in, update the sign-in date in the database, send a message to the user, and update the counter
                user.update_next_checkin_time()
                await Database.insert_or_replace(user)
                if message is not None:
                    await cls._send_message(bot, user, message)
                    cls._total[host] += 1
                    cls._honkai_count[host] += int(user.has_honkai3rd)
                    cls._starrail_count[host] += int(user.has_starrail)
                    cls._zzz_count[host] += int(user.has_zzz)
                    cls._themis_count[host] += int(user.has_themis) + int(user.has_themis_tw)
                    await asyncio.sleep(config.schedule_loop_delay)
            finally:
                queue.task_done()

    @classmethod
    async def _claim_daily_reward(cls, host: str, user: ScheduleDailyCheckin) -> str | None:
        
        """Perform daily check-ins for users.

        Parameters
        ----------
        host: `str`
            Signed in host
            - Local: Fixed as a string "LOCAL"
            - Remote: Check-in API URL
        user: `ScheduleDailyCheckin`
            Users who need to sign in

        Returns
        -------
        str | None
            Sign-in result message; None means skipping this user.

        Raises
        ------
        Exception
            If the sign-in fails, an Exception will be thrown.
        """
        if host == "LOCAL":  # Local Check-in
            message = await claim_daily_reward(
                user.discord_id,
                has_genshin=user.has_genshin,
                has_honkai3rd=user.has_honkai3rd,
                has_starrail=user.has_starrail,
                has_zzz=user.has_zzz,
                has_themis=user.has_themis,
                has_themis_tw=user.has_themis_tw,
            )
            return message
        else:  # Remote API Sign-in
            # In order to have cookies, the User Table data is obtained from the database.
            user_data = await Database.select_one(User, User.discord_id.is_(user.discord_id))
            gt_challenge = await Database.select_one(
                GeetestChallenge, GeetestChallenge.discord_id.is_(user.discord_id)
            )
            if user_data is None:
                return None
            check, msg = await database.Tool.check_user(user_data)
            if check is False:
                return msg
            payload: dict[str, Any] = {
                "discord_id": user.discord_id,
                "uid": 0,
                "cookie": user_data.cookie_default,
                "cookie_genshin": user_data.cookie_genshin,
                "cookie_honkai3rd": user_data.cookie_honkai3rd,
                "cookie_starrail": user_data.cookie_starrail,
                "cookie_zzz": user_data.cookie_zzz,
                "cookie_themis": user_data.cookie_themis,
                "has_genshin": "true" if user.has_genshin else "false",
                "has_honkai": "true" if user.has_honkai3rd else "false",
                "has_starrail": "true" if user.has_starrail else "false",
                "has_zzz": "true" if user.has_zzz else "false",
                "has_themis": "true" if user.has_themis else "false",
                "has_themis_tw": "true" if user.has_themis_tw else "false",
            }
            if gt_challenge is not None:
                payload.update(
                    {
                        "geetest_genshin": gt_challenge.genshin,
                        "geetest_honkai3rd": gt_challenge.honkai3rd,
                        "geetest_starrail": gt_challenge.starrail,
                    }
                )
            async with aiohttp.ClientSession() as session:
                async with session.post(url=host + "/daily-reward", json=payload) as resp:
                    if resp.status == 200:
                        result: dict[str, str] = await resp.json()
                        message = result.get("message", "Remote API sign-in failed")
                        return message
                    else:
                        raise Exception(f"{host} Sign-in failed, HTTP status code：{resp.status}")

    @classmethod
    async def _send_message(cls, bot: commands.Bot, user: ScheduleDailyCheckin, message: str):
        """Send a message to the user about the sign-in result"""
        try:
            _id = user.discord_channel_id
            channel = bot.get_channel(_id) or await bot.fetch_channel(_id)
            # If you don't mention the user with @, get the user's name first and then send the message
            if user.is_mention is False and "Cookie has expired" not in message:
                _user = await bot.fetch_user(user.discord_id)
                await channel.send(embed=EmbedTemplate.normal(f"[Automatic sign-in] {_user.name}：{message}"))  # type: ignore
            else:  # If you need to @mention the user or the cookie has expired
                await channel.send(f"<@{user.discord_id}>", embed=EmbedTemplate.normal(f"[Automatic sign-in] {message}"))  # type: ignore
        except (
            discord.Forbidden,
            discord.NotFound,
            discord.InvalidData,
        ) as e:  # Failed to send message, remove this user
            LOG.Except(f"Automatic sign-in message failed to be sent, remove this user {LOG.User(user.discord_id)}：{e}")
            await Database.delete_instance(user)
        except Exception as e:
            sentry_sdk.capture_exception(e)
