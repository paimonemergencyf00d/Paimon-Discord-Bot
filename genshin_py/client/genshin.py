import asyncio
from typing import Sequence, Tuple

import genshin

from database import GenshinSpiralAbyss

from ..errors_decorator import generalErrorHandler
from .common import get_client


@generalErrorHandler
async def get_genshin_notes(user_id: int) -> genshin.models.Notes:
    """Get user's instant notes

    Parameters
    ------
    user_id: `int`
        User Discord ID

    Returns
    ------
    `Notes`
        Query results
    """
    client = await get_client(user_id)
    return await client.get_genshin_notes(client.uid)


@generalErrorHandler
async def get_genshin_spiral_abyss(user_id: int, previous: bool = False) -> GenshinSpiralAbyss:
    """Get information about the Abyss

    Parameters
    ------
    user_id: `int`
        User Discord ID
    previous: `bool`
        `True`Query the previous issue's information, `False` query the current issue's information

    Returns
    ------
    `SpiralAbyssData`
        Query results
    """
    client = await get_client(user_id)
    try:
        await client.get_partial_genshin_user(client.uid or 0)  # refresh user data
    except Exception:
        pass
    abyss, characters = await asyncio.gather(
        client.get_genshin_spiral_abyss(client.uid or 0, previous=previous),
        client.get_genshin_characters(client.uid or 0),
        return_exceptions=True,
    )
    if isinstance(abyss, BaseException):
        raise abyss
    if isinstance(characters, BaseException):
        return GenshinSpiralAbyss(user_id, abyss.season, abyss, None)
    return GenshinSpiralAbyss(user_id, abyss.season, abyss, characters)


@generalErrorHandler
async def get_genshin_traveler_diary(user_id: int, month: int) -> genshin.models.Diary:
    """Get user traveler notes

    Parameters
    ------
    user_id: `int`
        User Discord ID
    month: `int`
        Month to query

    Returns
    ------
    `Diary`
        Query results
    """
    client = await get_client(user_id)
    diary = await client.get_diary(client.uid, month=month)
    return diary


@generalErrorHandler
async def get_genshin_record_card(
    user_id: int,
) -> Tuple[int, genshin.models.PartialGenshinUserStats]:
    """Get user record cards (achievements, active days, number of characters, divine pupils, number of treasure chests, etc.))

    Parameters
    ------
    user_id: `int`
        User Discord ID

    Returns
    ------
    `(int, PartialGenshinUserStats)`
        Query results, including UID and Genshin Impact user information
    """
    client = await get_client(user_id)
    userstats = await client.get_partial_genshin_user(client.uid or 0)
    return (client.uid or 0, userstats)


@generalErrorHandler
async def get_genshin_characters(user_id: int) -> Sequence[genshin.models.Character]:
    """Get all the user's role information

    Parameters
    ------
    user_id: `int`
        User Discord ID

    Returns
    ------
    `Sequence[Character]`
        Query results
    """
    client = await get_client(user_id)
    return await client.get_genshin_characters(client.uid or 0)


@generalErrorHandler
async def get_genshin_notices() -> Sequence[genshin.models.Announcement]:
    """Get in-game announcements

    Returns
    ------
    `Sequence[Announcement]`
        Announcement query results
    """
    client = genshin.Client(lang="en-us")
    notices = await client.get_genshin_announcements()
    return notices
