import discord
import genshin

from database import Database, User
from utility import get_day_of_week


async def parse_zzz_notes(
    notes: genshin.models.ZZZNotes,
    user: discord.User | discord.Member | None = None,
) -> discord.Embed:
    """Parse the data of the instant note and format the content into the discord embed format and send it back"""
    # Power
    battery_title = f"Current power：{notes.battery_charge.current}/{notes.battery_charge.max}"
    if notes.battery_charge.is_full:
        recovery_time = "已充滿！"
    else:
        day_msg = get_day_of_week(notes.battery_charge.full_datetime)
        recovery_time = f"{day_msg} {notes.battery_charge.full_datetime.strftime('%H:%M')}"
    battery_msg = f"Recovery time：{recovery_time}\n"

    video_state_map = {
        genshin.models.VideoStoreState.REVENUE_AVAILABLE: "To be settled",
        genshin.models.VideoStoreState.WAITING_TO_OPEN: "Waiting for business",
        genshin.models.VideoStoreState.CURRENTLY_OPEN: "Open now",
    }
    battery_msg += f"Daily active：{notes.engagement.current}/{notes.engagement.max}\n"
    battery_msg += f"Scratch Lottery　：{'Completed' if notes.scratch_card_completed else 'Unfinished'}\n"
    battery_msg += f"Video Store：{video_state_map.get(notes.video_store_state, '')}\n"

    # Based on the amount of power, the embed color changes from green (0x28c828) to yellow (0xc8c828) and then to red (0xc82828) with half of the power being used as the boundary.
    battery = notes.battery_charge.current
    max_half = notes.battery_charge.max / 2
    color = (
        0x28C828 + 0x010000 * int(0xA0 * battery / max_half)
        if battery < max_half
        else 0xC8C828 - 0x000100 * int(0xA0 * (battery - max_half) / max_half)
    )

    embed = discord.Embed(color=color)
    embed.add_field(name=battery_title, value=battery_msg, inline=False)

    if user is not None:
        _u = await Database.select_one(User, User.discord_id.is_(user.id))
        uid = str(_u.uid_zzz if _u else "")
        embed.set_author(
            name=f"Zenless Zone Zero {uid}",
            icon_url=user.display_avatar.url,
        )
    return embed
