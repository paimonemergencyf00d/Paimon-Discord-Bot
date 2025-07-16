import asyncio
from datetime import datetime
from typing import Awaitable, Callable, ClassVar

import discord
import sentry_sdk
import sqlalchemy
from discord.ext import commands

from database import Database, GenshinScheduleNotes, StarrailScheduleNotes, ZZZScheduleNotes
from utility import LOG, config

from .common import CheckResult, T_User
from .genshin import check_genshin_notes
from .starrail import check_starrail_notes
from .zzz import check_zzz_notes


class RealtimeNotes:
    """Types of automatic scheduling

    Methods
    -----
    execute(bot: `commands.Bot`)
        Execute automatic scheduling
    """

    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()
    _bot: commands.Bot

    @classmethod
    async def execute(cls, bot: commands.Bot):
        """Execute automatic scheduling

        Parameters
        -----
        bot: `commands.Bot`
            Discord bot client
        """
        if cls._lock.locked():
            return
        await cls._lock.acquire()
        cls._bot = bot
        try:
            LOG.System("Automatic resin check start")
            await asyncio.gather(
                cls._check_games_note(GenshinScheduleNotes, "Genshin Impact", check_genshin_notes),
                cls._check_games_note(StarrailScheduleNotes, "Honkai: Star Rail", check_starrail_notes),
                cls._check_games_note(ZZZScheduleNotes, "Zenless Zone Zero", check_zzz_notes),
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            LOG.Error(f"Automatically scheduled Realtime Notes Error: {e}")
        finally:
            cls._lock.release()

    @classmethod
    async def _check_games_note(
        cls,
        game_orm: type[T_User],
        game_name: str,
        game_check_fucntion: Callable[[T_User], Awaitable[CheckResult | None]],
    ) -> None:
        """Check all users' instant notes for a specific game

        Parameters
        ----------
        game_orm: Type[`T_User`]
            Scheduled check of instant notes ORM (Object association mapping) type
        game_name: `str`
            Game Title
        game_check_function: Callable[[`T_User`], Awaitable[`CheckResult` | `None`]]
           Function to check game notes

        """
        count = 0
        # Select All User IDs
        stmt = sqlalchemy.select(game_orm.discord_id)
        async with Database.sessionmaker() as session:
            user_ids = (await session.execute(stmt)).scalars().all()
        for user_id in user_ids:
            # Get the user to be checked. If the check time has not yet arrived, skip it.
            user = await Database.select_one(game_orm, game_orm.discord_id.is_(user_id))
            if user is None or user.next_check_time and datetime.now() < user.next_check_time:
                continue
            r = await game_check_fucntion(user)
            if r is not None:
                count += 1
            # Send messages to users when there are error messages or when the instant note is almost full
            if r and len(r.message) > 0:
                await cls._send_message(user, r.message, r.embed)
            # Check interval between users
            await asyncio.sleep(config.schedule_loop_delay)
        LOG.System(f"{game_name}Automatically check for instant note ending，{count}/{len(user_ids)} People have checked")

    @classmethod
    async def _send_message(cls, user: T_User, message: str, embed: discord.Embed) -> None:
        """Send message to remind users"""
        bot = cls._bot
        try:
            _id = user.discord_channel_id
            channel = bot.get_channel(_id) or await bot.fetch_channel(_id)
            discord_user = bot.get_user(user.discord_id) or await bot.fetch_user(user.discord_id)
            msg_sent = await channel.send(f"{discord_user.mention}，{message}", embed=embed)  # type: ignore
        except (
            discord.Forbidden,
            discord.NotFound,
            discord.InvalidData,
        ) as e:  # Failed to send message, remove this user
            LOG.Except(
                f"Automatically check instant notes to send messages. Failed to remove this user. {LOG.User(user.discord_id)}：{e}"
            )
            await Database.delete_instance(user)
        except Exception as e:
            sentry_sdk.capture_exception(e)
        else:  # Message sent successfully
            # Remove if the user is not in the channel where the message was sent
            if discord_user.mentioned_in(msg_sent) is False:
                LOG.Except(
                    f"Automatically check if the instant note user is not in the channel and remove the user {LOG.User(discord_user)}"
                )
                await Database.delete_instance(user)
