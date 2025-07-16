import random

from io import BytesIO
from pathlib import Path
from typing import Sequence

import aiohttp
import enkanetwork
import genshin
from PIL import Image, ImageDraw

from database.dataclass import spiral_abyss
from utility import get_server_name

from .common import draw_avatar, draw_text

__all__ = ["draw_abyss_card", "draw_exploration_card", "draw_record_card"]


def draw_rounded_rect(img: Image.Image, pos: tuple[float, float, float, float], **kwargs):
    """Draw a semi-transparent rounded rectangle"""
    transparent = Image.new("RGBA", img.size, 0)
    draw = ImageDraw.Draw(transparent, "RGBA")
    draw.rounded_rectangle(pos, **kwargs)
    img.paste(Image.alpha_composite(img, transparent))


def draw_basic_card(
    avatar_bytes: bytes, uid: int, user_stats: genshin.models.PartialGenshinUserStats
) -> Image.Image:
    img: Image.Image = Image.open(f"data/image/record_card/{random.randint(1, 12)}.jpg")
    img = img.convert("RGBA")

    avatar: Image.Image = Image.open(BytesIO(avatar_bytes)).resize((250, 250))
    draw_avatar(img, avatar, (70, 100))

    draw_rounded_rect(img, (340, 130, 990, 320), radius=30, fill=(0, 0, 0, 120))
    draw_rounded_rect(img, (90, 380, 990, 1810), radius=30, fill=(0, 0, 0, 120))

    info = user_stats.info
    draw_text(img, (665, 195), info.nickname, "SourceHanSerifTC-Bold.otf", 88, (255, 255, 255, 255), "mm")
    draw_text(
        img,
        (665, 275),
        f"{get_server_name(info.server)}  Lv.{info.level}  UID:{uid}",
        "SourceHanSansTC-Medium.otf",
        40,
        (255, 255, 255, 255),
        "mm",
    )

    return img


def draw_record_card(
    avatar_bytes: bytes, uid: int, user_stats: genshin.models.PartialGenshinUserStats
) -> BytesIO:
    """Make a personal record card

    ------
    Parameters
    avatar_bytes `bytes`: Discord user's avatar image, passed in bytes
    uid `int`: Genshin Impact Character UID
    user_stats `PartialGenshinUserStats`: User game records obtained from Hoyolab
    ------
    Returns
    `BytesIO`: The finished image is stored in the memory and the file pointer is returned.`seek(0)`
    """
    img = draw_basic_card(avatar_bytes, uid, user_stats)

    white = (255, 255, 255, 255)
    grey = (230, 230, 230, 255)

    s = user_stats.stats
    stat_list = [
        (s.days_active, "Active days"),
        (s.achievements, "Achievements"),
        (s.characters, "Characters"),
        (s.anemoculi, "Wind"),
        (s.geoculi, "Geo"),
        (s.electroculi, "Thunder"),
        (s.dendroculi, "Grass"),
        (s.hydroculi, "Water"),
        (s.pyroculi, "Fire"),
        (s.unlocked_waypoints, "Unlocked waypoints"),
        (s.unlocked_domains, "Unlocked secret realms"),
        (s.spiral_abyss, "Abyss"),
        (s.luxurious_chests, "Number of luxurious chests"),
        (s.precious_chests, "Number of precious chests"),
        (s.exquisite_chests, "Number of exquisite chests"),
        (s.common_chests, "Number of common treasure chests"),
        (s.remarkable_chests, "Number of remarkable treasure chests"),
    ]

    for n, stat in enumerate(stat_list):
        column = int(n % 3)
        row = int(n / 3)
        draw_text(
            img,
            (245 + column * 295, 500 + row * 210),
            str(stat[0]),
            "SourceHanSansTC-Bold.otf",
            80,
            white,
            "mm",
        )
        draw_text(
            img,
            (245 + column * 295, 570 + row * 210),
            str(stat[1]),
            "SourceHanSansTC-Regular.otf",
            40,
            grey,
            "mm",
        )

    img = img.convert("RGB")
    fp = BytesIO()
    img.save(fp, "jpeg", optimize=True, quality=50)
    return fp


def draw_exploration_card(
    avatar_bytes: bytes, uid: int, user_stats: genshin.models.PartialGenshinUserStats
) -> BytesIO:
    """Create a personal world exploration card

    ------
    Parameters
    avatar_bytes `bytes`: Discord user's avatar image, passed in bytes
    uid `int`: Genshin character UID
    user_stats `PartialGenshinUserStats`: User game records obtained from Hoyolab
    ------
    Returns
    `BytesIO`: The created image is stored in memory, and the file pointer is returned. `seek(0)` is required before access
    """
    img = draw_basic_card(avatar_bytes, uid, user_stats)

    white = (255, 255, 255, 255)
    grey = (230, 230, 230, 255)

    explored_list = {  # {id: [地名, 探索度]}
        1: ["Mondstadt", 0],
        2: ["Liyue", 0],
        3: ["Snow Mountain", 0],
        4: ["Inazuma", 0],
        5: ["Abyssal Palace", 0],
        6: ["Layer Rock·Surface", 0],
        7: ["Layer Rock·Bottom", 0],
        8: ["Sumeru", 0],
        9: ["Fontaine", 0],
        12: ["Sunken Jade Valley·Nanling", 0],
        13: ["Sunken Jade Valley·Upper Valley", 0],
        14: ["Old Sea", 0],
        15: ["Natta", 0],
    }
    offering_list = [["Honeysuckle Tree", 0], ["God's Favor", 0], ["Lumen Stone", 0], ["Dream Tree", 0], ["Lujing Spring", 0], ["Stone Fire", 0]]

    for e in user_stats.explorations:
        if e.id not in explored_list:
            continue
        explored_list[e.id][1] = e.explored

        if e.id == 3 and len(e.offerings) >= 1: # 3: Snow Mountain
            offering_list[0][1] = e.offerings[0].level
        if e.id == 4 and len(e.offerings) >= 2: # 4: rice wife
            offering_list[1][1] = e.offerings[0].level
        if e.id == 6 and len(e.offerings) >= 1: # 6: layer rock table
            offering_list[2][1] = e.offerings[0].level
        if e.id == 8 and len(e.offerings) >= 2: # 8: Xumi
            offering_list[3][1] = e.offerings[0].level
        if e.id == 9 and len(e.offerings) >= 2: # 9: Fontaine
            offering_list[4][1] = e.offerings[0].level
        if e.id == 15 and len(e.offerings) >= 1: # 15: Natta
            offering_list[5][1] = e.offerings[0].level

    stat_list: list[tuple[str, float, str]] = []  # (探索/等級, 數值, 地名)
    for id, e in explored_list.items():
        stat_list.append(("Explore", e[1], e[0]))
    for o in offering_list:
        stat_list.append(("Level", o[1], o[0]))

    for n, stat in enumerate(stat_list):
        column = int(n % 3)
        row = int(n / 3)
        draw_text(
            img,
            (245 + column * 295, 430 + row * 200),
            stat[0],
            "SourceHanSansTC-Regular.otf",
            30,
            grey,
            "mm",
        )
        draw_text(
            img,
            (245 + column * 295, 483 + row * 200),
            f"{stat[1]:g}",
            "SourceHanSansTC-Bold.otf",
            82,
            white,
            "mm",
        )
        draw_text(
            img,
            (245 + column * 295, 550 + row * 200),
            stat[2],
            "SourceHanSansTC-Regular.otf",
            45,
            grey,
            "mm",
        )

    img = img.convert("RGB")
    fp = BytesIO()
    img.save(fp, "jpeg", optimize=True, quality=50)
    return fp


async def draw_character(
    img: Image.Image,
    character: genshin.models.AbyssCharacter,
    size: tuple[int, int],
    pos: tuple[int, int],
):
    """Draw the character portrait, including the background frame

    ------
    Parameters
    character `AbyssCharacter`: character information
    size `Tuple[int, int]`: background frame size
    pos `Tuple[int, int]`: the upper left corner position to be drawn
    """
    background = (
        Image.open(f"data/image/character/char_{character.rarity}star_bg.png")
        .convert("RGBA")
        .resize(size)
    )
    avatar_file = Path(f"data/image/character/{character.id}.png")
    # 若本地沒有圖檔則從URL下載
    if avatar_file.exists() is False:
        avatar_img: bytes | None = None
        async with aiohttp.ClientSession() as session:
            # 嘗試從 Enkanetwork CDN 取得圖片
            try:
                enka_cdn = enkanetwork.Assets.character(character.id).images.icon.url  # type: ignore
            except Exception:
                pass
            else:
                async with session.get(enka_cdn) as resp:
                    if resp.status == 200:
                        avatar_img = await resp.read()
            # 當從 Enkanetwork CDN 取得圖片失敗時改用 Ambr
            if avatar_img is None:
                icon_name = character.icon.split("/")[-1]  # UI_AvatarIcon_XXXX.png
                ambr_url = "https://api.ambr.top/assets/UI/" + icon_name
                async with session.get(ambr_url) as resp:
                    if resp.status == 200:
                        avatar_img = await resp.read()
        if avatar_img is None:
            return
        else:
            with open(avatar_file, "wb") as fp:
                fp.write(avatar_img)
    avatar = Image.open(avatar_file).convert("RGBA").resize((size[0], size[0]))
    img.paste(background, pos, background)
    img.paste(avatar, pos, avatar)


def draw_abyss_star(
    img: Image.Image, number: int, size: tuple[int, int], pos: tuple[float, float]
):
    """Draw the number of abyss stars

    ------
    Parameters
    number `int`: number of stars
    size `Tuple[int, int]`: size of a single star
    pos `Tuple[float, float]`: the exact center position, the star will be automatically centered
    """
    star = Image.open("data/image/spiral_abyss/star.png").convert("RGBA").resize(size)
    pad = 5
    upper_left = (pos[0] - number / 2 * size[0] - (number - 1) * pad, pos[1] - size[1] / 2)
    for i in range(0, number):
        img.paste(star, (int(upper_left[0] + i * (size[0] + 2 * pad)), int(upper_left[1])), star)


async def draw_abyss_card(
    abyss_floor: genshin.models.Floor,
    characters: Sequence[spiral_abyss.CharacterData] | None = None,
) -> BytesIO:
    """Draw a record of the Abyss floors, including the number of stars in each room and the characters and levels used in the upper and lower halves

    ------
    Parameters
    abyss_floor `Floor`: Data of a floor in the Abyss Spiral
    characters `Sequence[Character]`: Player's character data
    ------
    Returns
    `BytesIO`: The finished image is stored in memory, and the file pointer is returned. `seek(0)` is required before access
    """
    img = Image.open("data/image/spiral_abyss/background_blur.jpg")
    img = img.convert("RGBA")

    character_size = (172, 210)
    character_pad = 8
    # Display the abyss level
    draw_text(
        img,
        (1050, 145),
        f"{abyss_floor.floor}",
        "SourceHanSansTC-Bold.otf",
        85,
        (50, 50, 50),
        "mm",
    )
    # Draw each
    for i, chamber in enumerate(abyss_floor.chambers):
        # Show the number of stars in this room
        draw_abyss_star(img, chamber.stars, (70, 70), (1050, 500 + i * 400))
        # Upper and lower rooms
        for j, battle in enumerate(chamber.battles):
            middle = 453 + j * 1196
            left_upper = (
                int(
                    middle
                    - len(battle.characters) / 2 * character_size[0]
                    - (len(battle.characters) - 1) * character_pad
                ),
                395 + i * 400,
            )
            for k, character in enumerate(battle.characters):
                x = left_upper[0] + k * (character_size[0] + 2 * character_pad)
                y = left_upper[1]
                await draw_character(img, character, (172, 210), (x, y))
                if characters is not None:
                    constellation = next(
                        (c.constellation for c in characters if c.id == character.id), 0
                    )  # Match character ID and get constellation
                    text = f"{constellation}life {character.level}class"
                else:
                    text = f"{character.level}class"
                draw_text(
                    img,
                    (x + character_size[0] / 2, y + character_size[1] * 0.90),
                    text,
                    "SourceHanSansTC-Regular.otf",
                    30,
                    (50, 50, 50),
                    "mm",
                )
    img = img.convert("RGB")
    fp = BytesIO()
    img.save(fp, "jpeg", optimize=True, quality=40)
    return fp
