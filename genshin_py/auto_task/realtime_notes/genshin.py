from datetime import datetime, timedelta

import genshin

from database import Database, GenshinScheduleNotes
from utility import EmbedTemplate

from ... import parse_genshin_notes
from .common import CheckResult, cal_next_check_time, get_realtime_notes


async def check_genshin_notes(user: GenshinScheduleNotes) -> CheckResult | None:
    """Check the instant notes according to each user's settings. If the setting value is exceeded, a reminder message will be returned. If this user is skipped, None will be returned."""
    try:
        notes = await get_realtime_notes(user)
    except Exception as e:
        return CheckResult("An error occurred while Genshin Impact was automatically checking instant notes. We plan to check again in 5 hours.", EmbedTemplate.error(e))

    if not isinstance(notes, genshin.models.Notes):
        return None

    msg = await check_threshold(user, notes)
    embed = await parse_genshin_notes(notes, short_form=True)
    return CheckResult(msg, embed)


async def check_threshold(user: GenshinScheduleNotes, notes: genshin.models.Notes) -> str:
    msg = ""
    next_check_time: list[datetime] = [datetime.now() + timedelta(days=1)]  # Set a basic next check time
    # Function to calculate the next inspection time: estimated completion time - user-set time

    # Check the resin
    if isinstance(user.threshold_resin, int):
        # When the resin is less than the set value, set the message to be sent.
        if notes.remaining_resin_recovery_time <= timedelta(
            hours=user.threshold_resin, seconds=10
        ):
            msg += (
                "The resin is full!" if notes.remaining_resin_recovery_time <= timedelta(0) else "Resin is almost full!"
            )
        # Set the next inspection time. When the resin is fully filled, it is expected to be inspected again in 6 hours; otherwise, it is based on (estimated completion-user set time)
        next_check_time.append(
            datetime.now() + timedelta(hours=6)
            if notes.current_resin >= notes.max_resin
            else cal_next_check_time(notes.remaining_resin_recovery_time, user.threshold_resin)
        )
    # Check the cave treasure money
    if isinstance(user.threshold_currency, int):
        if notes.remaining_realm_currency_recovery_time <= timedelta(
            hours=user.threshold_currency, seconds=10
        ):
            msg += (
                "The Dongtian treasure money is full!"
                if notes.remaining_realm_currency_recovery_time <= timedelta(0)
                else "The Dongtian treasure money is almost full!"
            )
        next_check_time.append(
            datetime.now() + timedelta(hours=6)
            if notes.current_realm_currency >= notes.max_realm_currency
            else cal_next_check_time(
                notes.remaining_realm_currency_recovery_time,
                user.threshold_currency,
            )
        )
    # Check the quality change instrument
    if (
        isinstance(user.threshold_transformer, int)
        and notes.remaining_transformer_recovery_time is not None
    ):
        if notes.remaining_transformer_recovery_time <= timedelta(
            hours=user.threshold_transformer, seconds=10
        ):
            msg += (
                "The transmutator is complete!"
                if notes.remaining_transformer_recovery_time <= timedelta(0)
                else "The Transmutator is almost done!"
            )
        next_check_time.append(
            datetime.now() + timedelta(hours=6)
            if notes.remaining_transformer_recovery_time.total_seconds() <= 5
            else cal_next_check_time(
                notes.remaining_transformer_recovery_time,
                user.threshold_transformer,
            )
        )
    # Check Explore Dispatch
    if isinstance(user.threshold_expedition, int) and len(notes.expeditions) > 0:
        # Select the dispatch with the most remaining time
        longest_expedition = max(notes.expeditions, key=lambda epd: epd.remaining_time)
        if longest_expedition.remaining_time <= timedelta(
            hours=user.threshold_expedition, seconds=10
        ):
            msg += (
                "The quest dispatch is complete!" if longest_expedition.remaining_time <= timedelta(0) else "Exploration dispatch is almost complete!"
            )
        next_check_time.append(
            datetime.now() + timedelta(hours=6)
            if longest_expedition.finished is True
            else cal_next_check_time(longest_expedition.remaining_time, user.threshold_expedition)
        )
    # Check daily order
    if isinstance(user.check_commission_time, datetime):
        # When the current time exceeds the set inspection time
        if datetime.now() >= user.check_commission_time:
            if not notes.claimed_commission_reward:
                msg += "Today's commission has not been completed yet!"
            # The next check time will be today + 1 day, and the database will be updated
            user.check_commission_time += timedelta(days=1)
        next_check_time.append(user.check_commission_time)

    # Set the next inspection time, taking the minimum value from the above set times
    check_time = min(next_check_time)
    # If a message needs to be sent this time, set the next check time to at least 1 hour
    if len(msg) > 0:
        check_time = max(check_time, datetime.now() + timedelta(minutes=60))
    user.next_check_time = check_time
    await Database.insert_or_replace(user)

    return msg
