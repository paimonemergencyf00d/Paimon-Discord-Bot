from datetime import datetime, timedelta
from typing import NamedTuple, TypeVar

import discord
import genshin

from database import Database, GenshinScheduleNotes, StarrailScheduleNotes, ZZZScheduleNotes

from ... import errors, get_genshin_notes, get_starrail_notes, get_zzz_notes

T_User = TypeVar("T_User", GenshinScheduleNotes, StarrailScheduleNotes, ZZZScheduleNotes)


class CheckResult(NamedTuple):
    """`tuple[str, embed]`: The return result of the check_xxx_notes function"""

    message: str
    embed: discord.Embed


async def get_realtime_notes(
    user: T_User,
) -> genshin.models.Notes | genshin.models.StarRailNote | genshin.models.ZZZNotes | None:
    """Gets the instant note according to the passed user. If an exception other than InternalDatabaseError occurs, it will be thrown"""
    notes = None
    try:
        if isinstance(user, GenshinScheduleNotes):
            notes = await get_genshin_notes(user.discord_id)
        if isinstance(user, StarrailScheduleNotes):
            notes = await get_starrail_notes(user.discord_id)
        if isinstance(user, ZZZScheduleNotes):
            notes = await get_zzz_notes(user.discord_id)
    except Exception as e:
        # When the error is InternalDatabaseError, ignore it and set a check after 1 hour
        if isinstance(e, errors.GenshinAPIException) and isinstance(
            e.origin, genshin.errors.InternalDatabaseError
        ):
            user.next_check_time = datetime.now() + timedelta(hours=1)
            await Database.insert_or_replace(user)
        # When the error triggers a graphic validation error, set the check to occur after 24 hours
        elif isinstance(e, errors.GenshinAPIException) and isinstance(
            e.origin, genshin.errors.GeetestError
        ):
            user.next_check_time = datetime.now() + timedelta(hours=24)
            await Database.insert_or_replace(user)
            raise e
        else:  # When an error occurs, expect to check again after 5 hours
            user.next_check_time = datetime.now() + timedelta(hours=5)
            await Database.insert_or_replace(user)
            raise e
    return notes


def cal_next_check_time(remaining: timedelta, user_threshold: int) -> datetime:
    """Function to calculate the next check time

    Parameters
    ------
    remaining: `timedelta`:
        time left
    user_threshold: `int`
        The reminder threshold set by the user, in hours.

    Returns
    ------
    `datetime`:
        The time of next inspection.
    """
    remaining_hours: float = remaining.total_seconds() / 3600
    if remaining_hours > user_threshold:
        # If the remaining time is longer than the reminder time set by the user, the time point set by the user will be returned.
        return datetime.now() + remaining - timedelta(hours=user_threshold)
    else:  # remaining <= user_threshold
        # When the remaining time is short, we take 3 intervals as the reminder time
        # For example, if the user sets a reminder 24 hours in advance, the next reminder time will be 16, 8, or 0 hours in advance.
        interval: float = float(user_threshold / 3)
        user_threshold_f: float = float(user_threshold)
        if interval > 0.0:
            while remaining_hours <= user_threshold_f:
                user_threshold_f -= interval
        return datetime.now() + remaining - timedelta(hours=user_threshold_f)
