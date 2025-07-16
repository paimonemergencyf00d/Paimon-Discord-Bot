from datetime import datetime, timedelta

import genshin

from database import Database, StarrailScheduleNotes
from utility import EmbedTemplate

from ... import errors, parse_starrail_notes
from .common import CheckResult, cal_next_check_time, get_realtime_notes


async def check_starrail_notes(user: StarrailScheduleNotes) -> CheckResult | None:
    """Check the instant notes according to each user's settings. If the setting value is exceeded, a reminder message will be returned. If this user is skipped, None will be returned."""
    try:
        notes = await get_realtime_notes(user)
    except Exception as e:
        if isinstance(e, errors.GenshinAPIException) and isinstance(e.origin, genshin.errors.GeetestError):
            return CheckResult("An error occurred while Star Dome Railway was automatically checking instant notes. We plan to check again in 24 hours.", EmbedTemplate.error(e))
        else:
            return CheckResult("An error occurred while Star Dome Railway was automatically checking instant notes. We plan to check again in 5 hours.", EmbedTemplate.error(e))

    if not isinstance(notes, genshin.models.StarRailNote):
        return None

    msg = await check_threshold(user, notes)
    embed = await parse_starrail_notes(notes, short_form=True)
    return CheckResult(msg, embed)


async def check_threshold(user: StarrailScheduleNotes, notes: genshin.models.StarRailNote) -> str:
    msg = ""
    # Set a basic next check time
    next_check_time: list[datetime] = [datetime.now() + timedelta(days=1)]

    # Check the pioneering ability
    if isinstance(user.threshold_power, int):
        # When the time until the development force reaches the full limit is lower than the set value, set the message to be sent
        if notes.stamina_recover_time <= timedelta(hours=user.threshold_power):
            msg += "The pioneering power is full!" if notes.stamina_recover_time <= timedelta(0) else "Pioneering force is almost full!"
        next_check_time.append(
            datetime.now() + timedelta(hours=6)
            if notes.current_stamina >= notes.max_stamina
            else cal_next_check_time(notes.stamina_recover_time, user.threshold_power)
        )
    # Inspection Commission
    if isinstance(user.threshold_expedition, int) and len(notes.expeditions) > 0:
        longest_expedition = max(notes.expeditions, key=lambda epd: epd.remaining_time)
        if longest_expedition.remaining_time <= timedelta(hours=user.threshold_expedition):
            msg += "The commission has been completed!" if longest_expedition.remaining_time <= timedelta(0) else "The commission is almost complete!"
        next_check_time.append(
            datetime.now() + timedelta(hours=6)
            if longest_expedition.finished is True
            else cal_next_check_time(longest_expedition.remaining_time, user.threshold_expedition)
        )
    # Check daily training
    if isinstance(user.check_daily_training_time, datetime):
        # When the current time exceeds the set inspection time
        if datetime.now() >= user.check_daily_training_time:
            if notes.current_train_score < notes.max_train_score:
                msg += "Today's daily training is not yet completed!"
            # The next check time will be today + 1 day, and the database will be updated
            user.check_daily_training_time += timedelta(days=1)
        next_check_time.append(user.check_daily_training_time)
    # Check the simulated universe
    if isinstance(user.check_universe_time, datetime):
        # When the current time exceeds the set inspection time
        if datetime.now() >= user.check_universe_time:
            if notes.current_rogue_score < notes.max_rogue_score:
                msg += "This week's SimUniverse isn't done yet!"
            # The next inspection will be in the next week and the database will be updated
            user.check_universe_time += timedelta(weeks=1)
        next_check_time.append(user.check_universe_time)
    # Check the aftermath of the battle
    if isinstance(user.check_echoofwar_time, datetime):
        # When the current time exceeds the set inspection time
        if datetime.now() >= user.check_echoofwar_time:
            if notes.remaining_weekly_discounts > 0:
                msg += "This week's Aftermath isn't done yet!"
            # The next inspection will be in the next week and the database will be updated
            user.check_echoofwar_time += timedelta(weeks=1)
        next_check_time.append(user.check_echoofwar_time)

    # Set the next inspection time, taking the minimum value from the above set times
    check_time = min(next_check_time)
    # If a message needs to be sent this time, set the next check time to at least 1 hour
    if len(msg) > 0:
        check_time = max(check_time, datetime.now() + timedelta(minutes=60))
    user.next_check_time = check_time
    await Database.insert_or_replace(user)

    return msg
