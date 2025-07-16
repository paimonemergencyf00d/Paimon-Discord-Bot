from datetime import datetime, timedelta

import genshin

from database import Database, ZZZScheduleNotes
from utility import EmbedTemplate

from ... import parse_zzz_notes
from .common import CheckResult, cal_next_check_time, get_realtime_notes


async def check_zzz_notes(user: ZZZScheduleNotes) -> CheckResult | None:
    """Check the instant notes according to each user's settings. If the setting value is exceeded, a reminder message will be returned. If this user is skipped, None will be returned."""
    try:
        notes = await get_realtime_notes(user)
    except Exception as e:
        return CheckResult(
            "An error occurred while ZenlessZoneZero was automatically checking instant notes. It is expected to check again in 5 hours.", EmbedTemplate.error(e)
        )

    if not isinstance(notes, genshin.models.ZZZNotes):
        return None

    msg = await check_threshold(user, notes)
    embed = await parse_zzz_notes(notes)
    return CheckResult(msg, embed)


async def check_threshold(user: ZZZScheduleNotes, notes: genshin.models.ZZZNotes) -> str:
    msg = ""
    # Set a basic next check time
    next_check_time: list[datetime] = [datetime.now() + timedelta(days=1)]

    # Check the battery level
    if isinstance(user.threshold_battery, int):
        # When the battery time to full capacity is lower than the set value, set the message to be sent
        if timedelta(seconds=notes.battery_charge.seconds_till_full) <= timedelta(
            hours=user.threshold_battery
        ):
            msg += "The battery is fully charged!" if notes.battery_charge.is_full else "The battery is almost fully charged!"
        next_check_time.append(
            datetime.now() + timedelta(hours=6)
            if notes.battery_charge.is_full
            else cal_next_check_time(
                timedelta(seconds=notes.battery_charge.seconds_till_full), user.threshold_battery
            )
        )
    # Check today's activity
    if isinstance(user.check_daily_engagement_time, datetime):
        # When the current time exceeds the set inspection time
        if datetime.now() >= user.check_daily_engagement_time:
            if notes.engagement.current < notes.engagement.max:
                msg += "Today's activity is not yet complete!"
            # The next check time will be today + 1 day, and the database will be updated
            user.check_daily_engagement_time += timedelta(days=1)
        next_check_time.append(user.check_daily_engagement_time)

    # Set the next inspection time, taking the minimum value from the above set times
    check_time = min(next_check_time)
    # If a message needs to be sent this time, set the next check time to at least 1 hour
    if len(msg) > 0:
        check_time = max(check_time, datetime.now() + timedelta(minutes=60))
    user.next_check_time = check_time
    await Database.insert_or_replace(user)

    return msg
