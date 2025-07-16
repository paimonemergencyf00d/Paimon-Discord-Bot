from datetime import datetime

import discord
import genshin

from database import Database, User
from utility import get_day_of_week, get_server_name


async def parse_starrail_notes(
    notes: genshin.models.StarRailNote,
    user: discord.User | discord.Member | None = None,
    *,
    short_form: bool = False,
) -> discord.Embed:
    """Parse the data of the instant note and format the content into the discord embed format and send it back"""
    # Pioneering
    stamina_title = f"Current development capabilities: {notes.current_stamina}/{notes.max_stamina}"
    if notes.current_reserve_stamina > 0:
        stamina_title += f" + {notes.current_reserve_stamina}"
    if notes.current_stamina >= notes.max_stamina:
        recovery_time = "Full!"
    else:
        day_msg = get_day_of_week(notes.stamina_recovery_time)
        recovery_time = f"{day_msg} {notes.stamina_recovery_time.strftime('%H:%M')}"
    stamina_msg = f"Recovery time:{recovery_time}\n"

    # Daily, Simulated Universe, Weekly
    stamina_msg += f"Daily training: {notes.current_train_score} / {notes.max_train_score}\n"
    stamina_msg += f"Simulated Universe: {notes.current_rogue_score} / {notes.max_rogue_score}\n"
    stamina_msg += f"Aftermath: The Remaining {notes.remaining_weekly_discounts} 次\n"

    # Entrusted execution
    exped_finished = 0
    exped_msg = ""
    for expedition in notes.expeditions:
        exped_msg += f"． {expedition.name}："
        if expedition.finished is True:
            exped_finished += 1
            exped_msg += "Completed\n"
        else:
            day_msg = get_day_of_week(expedition.completion_time)
            exped_msg += f"{day_msg} {expedition.completion_time.strftime('%H:%M')}\n"
    # Simple format with only the longest completion time
    if short_form is True and len(notes.expeditions) > 0:
        longest_expedition = max(notes.expeditions, key=lambda epd: epd.remaining_time)
        if longest_expedition.finished is True:
            exped_msg = "． Completion time: Completed\n"
        else:
            day_msg = get_day_of_week(longest_expedition.completion_time)
            exped_msg = (
                f"． Completion time: {day_msg} {longest_expedition.completion_time.strftime('%H:%M')}\n"
            )

    exped_title = f"Entrusted execution:{exped_finished}/{len(notes.expeditions)}"

    # According to the amount of pioneering power, the embed color changes from green to (0x28c828) Gradient to yellow (0xc8c828)，Then fade to red (0xc82828)
    stamina = notes.current_stamina
    max_half = notes.max_stamina / 2
    color = (
        0x28C828 + 0x010000 * int(0xA0 * stamina / max_half)
        if stamina < max_half
        else 0xC8C828 - 0x000100 * int(0xA0 * (stamina - max_half) / max_half)
    )

    embed = discord.Embed(color=color)
    embed.add_field(name=stamina_title, value=stamina_msg, inline=False)
    if exped_msg != "":
        embed.add_field(name=exped_title, value=exped_msg, inline=False)

    if user is not None:
        _u = await Database.select_one(User, User.discord_id.is_(user.id))
        uid = str(_u.uid_starrail if _u else "")
        embed.set_author(
            name=f"honkai:starrail {get_server_name(uid[0])} {uid}",
            icon_url=user.display_avatar.url,
        )
    return embed


def parse_starrail_diary(diary: genshin.models.StarRailDiary, month: int) -> discord.Embed:
    ...


def parse_starrail_character(character: genshin.models.StarRailDetailCharacter) -> discord.Embed:
    """Character analysis, including star soul, level, light cone, and relics"""
    color = {
        "physical": 0xC5C5C5,
        "fire": 0xF4634E,
        "ice": 0x72C2E6,
        "lightning": 0xDC7CF4,
        "wind": 0x73D4A4,
        "quantum": 0x9590E4,
        "imaginary": 0xF7E54B,
    }
    embed = discord.Embed(color=color.get(character.element.lower()))
    embed.set_thumbnail(url=character.icon)
    embed.add_field(
        name=f"★{character.rarity} {character.name}",
        inline=True,
        value=f"Star Soul：{character.rank}\ngrade：Lv. {character.level}",
    )
    if character.equip:
        lightcone = character.equip
        embed.add_field(
            name=f"Light cone：{lightcone.name}",
            inline=True,
            value=f"Overlap：{lightcone.rank} Tier\nLevel：Lv. {lightcone.level}",
        )

    if character.rank > 0:
        number = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
        msg = "\n".join(
            [f"No.{number[rank.pos]}layer：{rank.name}" for rank in character.ranks if rank.is_unlocked]
        )
        embed.add_field(name="Star Soul", inline=False, value=msg)

    if len(character.relics) > 0:
        pos_name = {1: "head", 2: "Hands", 3: "trunk", 4: "Feet"}
        msg = "\n".join(
            [
                f"{pos_name.get(relic.pos)}：★{relic.rarity} {relic.name}"
                for relic in character.relics
            ]
        )
        embed.add_field(name="Relics", inline=False, value=msg)

    if len(character.ornaments) > 0:
        pos_name = {5: "Dimensional Ball", 6: "Connecting rope"}
        msg = "\n".join(
            [
                f"{pos_name.get(ornament.pos)}：★{ornament.rarity} {ornament.name}"
                for ornament in character.ornaments
            ]
        )
        embed.add_field(name="accessories", inline=False, value=msg)
    return embed


def parse_starrail_hall_overview(
    hall: genshin.models.StarRailChallenge | genshin.models.StarRailPureFiction,
) -> discord.Embed:
    """Analysis of the Starry Sky Railway: Forgotten Garden overview information, including level progress, number of battles, number of stars obtained, and number of periods"""
    # Check Crown Eligibility
    has_crown: bool = False
    if isinstance(hall, genshin.models.StarRailChallenge):
        # The Forgotten Garden 2023/12/20 is 10 floors before and 12 floors after
        max_stars = 30 if hall.begin_time.datetime < datetime(2023, 12, 20) else 36
        if hall.total_stars == max_stars:
            non_skip_battles = [floor.is_quick_clear for floor in hall.floors].count(False)
            has_crown = hall.total_battles == non_skip_battles
    else:  # isinstance(hall, genshin.models.StarRailPureFiction)
        if hall.total_stars == 12:
            non_skip_battles = [floor.is_quick_clear for floor in hall.floors].count(False)
            has_crown = hall.total_battles == non_skip_battles
    battle_nums = f"👑 ({hall.total_battles})" if has_crown else hall.total_battles

    desc: str = (
        f"{hall.begin_time.datetime.strftime('%Y.%m.%d')} ~ {hall.end_time.datetime.strftime('%Y.%m.%d')}\n"
    )
    desc += f"Level Progress：{hall.max_floor}\n"
    desc += f"Number of battles：{battle_nums}　★：{hall.total_stars}\n"
    embed = discord.Embed(description=desc, color=0x934151)
    return embed
