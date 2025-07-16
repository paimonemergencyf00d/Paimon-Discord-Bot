from typing import Sequence, Union

import discord
import genshin

from database import Database, User
from utility import emoji, get_day_of_week, get_server_name


def parse_genshin_abyss_overview(abyss: genshin.models.SpiralAbyss) -> discord.Embed:
    """Parse the Abyss overview data, including date, number of layers, number of battles, total number of stars... etc.

    ------
    Parameters
    abyss `SpiralAbyss`: Spiral Abyss data
    ------
    Returns
    `discord.Embed`: discord embed format
    """
    result = discord.Embed(
        description=(
            f'No. {abyss.season} Expect：{abyss.start_time.astimezone().strftime("%Y.%m.%d")} ~ '
            f'{abyss.end_time.astimezone().strftime("%Y.%m.%d")}'
        ),
        color=0x6959C1,
    )

    crowned: bool = (
        True
        if abyss.max_floor == "12-3" and abyss.total_stars == 36 and abyss.total_battles == 12
        else False
    )

    def get_character_rank(c: Sequence[genshin.models.AbyssRankCharacter]):
        return " " if len(c) == 0 else f"{c[0].name}：{c[0].value}"

    result.add_field(
        name=f'Deepest Reach：{abyss.max_floor}　Number of battles：{"👑 (12)" if crowned else abyss.total_battles}　★：{abyss.total_stars}',
        value=f"[Maximum number of kills] {get_character_rank(abyss.ranks.most_kills)}\n"
        f"[The strongest blow] {get_character_rank(abyss.ranks.strongest_strike)}\n"
        f"[Most injured] {get_character_rank(abyss.ranks.most_damage_taken)}\n"
        f"[Q Cast Times] {get_character_rank(abyss.ranks.most_bursts_used)}\n"
        f"[E cast times] {get_character_rank(abyss.ranks.most_skills_used)}",
        inline=False,
    )
    return result


def parse_genshin_abyss_chamber(chamber: genshin.models.Chamber) -> str:
    """Get the character name of a chamber in the Abyss

    ------
    Parameters
    chamber `Chamber`: Information about a chamber in the Abyss
    ------
    Returns
    `str`: String consisting of the character name
    """
    chara_list: list[list[str]] = [[], []]  # Divided into upper and lower halves
    for i, battle in enumerate(chamber.battles):
        for chara in battle.characters:
            chara_list[i].append(chara.name)
    return f'{".".join(chara_list[0])} ／\n{".".join(chara_list[1])}'


def parse_genshin_character(character: genshin.models.Character) -> discord.Embed:
    """Analyze the character, including constellation, level, favorability, weapons, and relics

    ------
    Parameters
    character `Character`: character information
    ------
    Returns
    `discord.Embed`: discord embed format
    """
    color = {
        "pyro": 0xFB4120,
        "electro": 0xBF73E7,
        "hydro": 0x15B1FF,
        "cryo": 0x70DAF1,
        "dendro": 0xA0CA22,
        "anemo": 0x5CD4AC,
        "geo": 0xFAB632,
    }
    embed = discord.Embed(color=color.get(character.element.lower()))
    embed.set_thumbnail(url=character.icon)
    embed.add_field(
        name=f"★{character.rarity} {character.name}",
        inline=True,
        value=f"Constellation：{character.constellation}\ngrade：Lv. {character.level}\nFavorability：Lv. {character.friendship}",
    )

    weapon = character.weapon
    embed.add_field(
        name=f"★{weapon.rarity} {weapon.name}",
        inline=True,
        value=f"Refining：{weapon.refinement} Tier\nLevel：Lv. {weapon.level}",
    )

    if character.constellation > 0:
        number = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
        msg = "\n".join(
            [
                f"No.{number[constella.pos]}layer：{constella.name}"
                for constella in character.constellations
                if constella.activated
            ]
        )
        embed.add_field(name="Constellation", inline=False, value=msg)

    if len(character.artifacts) > 0:
        msg = "\n".join(
            [
                f"{artifact.pos_name}：{artifact.name} ({artifact.set.name})"
                for artifact in character.artifacts
            ]
        )
        embed.add_field(name="Holy Relics", inline=False, value=msg)

    return embed


def parse_genshin_diary(diary: genshin.models.Diary, month: int) -> discord.Embed:
    """Parse traveler log

    ------
    Parameters
    diary `Diary`: traveler log
    ------
    Returns
    `discord.Embed`: discord embed format
    """
    d = diary.data
    embed = discord.Embed(
        title=f"{diary.nickname} Traveler's Notes：{month}moon",
        description=f'Rough stone income compared to last month{"Increase" if d.current_primogems >= d.last_primogems else "reduce"}了{abs(d.primogems_rate)}%，'
        f'Mora's income is higher than last month{"Increase" if d.current_mora >= d.last_mora else "reduce"}了{abs(d.mora_rate)}%',
        color=0xFD96F4,
    )
    embed.add_field(
        name="The total amount received this month",
        value=f"{emoji.items.primogem}Rough Stone：{d.current_primogems} ({round(d.current_primogems/160)}{emoji.items.intertwined_fate})\n"
        f'{emoji.items.mora}Mora：{format(d.current_mora, ",")}',
    )
    embed.add_field(
        name="Last month received",
        value=f"{emoji.items.primogem}Rough Stone：{d.last_primogems} ({round(d.last_primogems/160)}{emoji.items.intertwined_fate})\n"
        f'{emoji.items.mora}Mora：{format(d.last_mora, ",")}',
    )
    embed.add_field(name="\u200b", value="\u200b")  # Blank Line

    # Divide the Notes Stone into two fields
    for i in range(0, 2):
        msg = ""
        length = len(d.categories)
        for j in range(round(length / 2 * i), round(length / 2 * (i + 1))):
            msg += f"{d.categories[j].name[0:2]}：{d.categories[j].amount} ({d.categories[j].percentage}%)\n"
        embed.add_field(name=f"Rough stone income composition {i+1}", value=msg, inline=True)

    embed.add_field(name="\u200b", value="\u200b")  # Blank Line

    return embed


async def parse_genshin_notes(
    notes: genshin.models.Notes,
    *,
    user: Union[discord.User, discord.Member, None] = None,
    short_form: bool = False,
) -> discord.Embed:
    """Parse the data of the instant note, format the content into the discord embedding format and return it

    ------
    Parameters
    notes `Notes`: the data of the instant note
    user `discord.User`: the Discord user
    short_form `bool`: set to `False`, resin, treasure money, parameter quality change instrument, dispatch, daily, and weekly are fully displayed; set to `True`, only resin, treasure money, and parameter quality change instrument are displayed
    ------
    Returns
    `discord.Embed`: discord embedding format
    """
    # Original resin
    resin_title = f"{emoji.notes.resin}Current raw resin：{notes.current_resin}/{notes.max_resin}\n"
    if notes.current_resin >= notes.max_resin:
        recover_time = "Full!"
    else:
        day_msg = get_day_of_week(notes.resin_recovery_time)
        recover_time = f'{day_msg} {notes.resin_recovery_time.strftime("%H:%M")}'
    resin_msg = f"{emoji.notes.resin}Total recovery time：{recover_time}\n"
    # Daily, Weekly
    resin_msg += f"{emoji.notes.commission}Daily commission tasks:"
    resin_msg += (
        "Reward received\n"
        if notes.claimed_commission_reward is True
        else "**Prize not yet claimed**\n"
        if notes.max_commissions == notes.completed_commissions
        else f"Remaining {notes.max_commissions - notes.completed_commissions} indivual\n"
    )
    if not short_form:
        resin_msg += (
            f"{emoji.notes.enemies_of_note}Weekly resin halved: remaining {notes.remaining_resin_discounts} Second-rate\n"
        )
    # Dongtian Treasure Money Recovery Time
    resin_msg += f"{emoji.notes.realm_currency}Current Cave Treasure Money:{notes.current_realm_currency}/{notes.max_realm_currency}\n"
    if not short_form and notes.max_realm_currency > 0:
        if notes.current_realm_currency >= notes.max_realm_currency:
            recover_time = "Full!"
        else:
            day_msg = get_day_of_week(notes.realm_currency_recovery_time)
            recover_time = f'{day_msg} {notes.realm_currency_recovery_time.strftime("%H:%M")}'
        resin_msg += f"{emoji.notes.realm_currency}Total recovery time:{recover_time}\n"
    # Parameter quality change instrument remaining time
    if (t := notes.remaining_transformer_recovery_time) is not None:
        if t.days > 0:
            recover_time = f"Remaining {t.days} sky"
        elif t.hours > 0:
            recover_time = f"Remaining{t.hours} Hour"
        elif t.minutes > 0:
            recover_time = f"Remaining{t.minutes} point"
        elif t.seconds > 0:
            recover_time = f"Remaining{t.seconds} Second"
        else:
            recover_time = "Available"
        resin_msg += f"{emoji.notes.transformer}Parameter quality change instrument　：{recover_time}\n"
    # Explore the remaining time for dispatch
    exped_finished = 0
    exped_msg = ""
    for expedition in notes.expeditions:
        exped_msg += "． "
        if expedition.finished:
            exped_finished += 1
            exped_msg += "Completed\n"
        else:
            day_msg = get_day_of_week(expedition.completion_time)
            exped_msg += f'{day_msg} {expedition.completion_time.strftime("%H:%M")}\n'

    exped_title = f"{emoji.notes.expedition}Explore dispatch results: {exped_finished}/{len(notes.expeditions)}\n"

    # According to the amount of resin, the embed color changes from green to(0x28c828)Gradient to yellow(0xc8c828)，Then fade to red(0xc82828)
    r = notes.current_resin
    h = notes.max_resin // 2
    color = (
        0x28C828 + 0x010000 * int(0xA0 * r / h)
        if r < 80
        else 0xC8C828 - 0x000100 * int(0xA0 * (r - h) / h)
    )
    embed = discord.Embed(color=color)

    if (not short_form) and (exped_msg != ""):
        embed.add_field(name=resin_title, value=resin_msg)
        embed.add_field(name=exped_title, value=exped_msg)
    else:
        embed.add_field(name=resin_title, value=(resin_msg + exped_title))

    if user is not None:
        _u = await Database.select_one(User, User.discord_id.is_(user.id))
        uid = str(_u.uid_genshin if _u else "")
        embed.set_author(
            name=f"Genshin Impact {get_server_name(uid[0])} {uid}",
            icon_url=user.display_avatar.url,
        )
    return embed
