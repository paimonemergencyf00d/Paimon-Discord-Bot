from io import BytesIO
from pathlib import Path

import aiohttp
import genshin
from PIL import Image

from .common import draw_avatar, draw_text

__all__ = ["draw_starrail_forgottenhall_card"]


async def draw_character(character: genshin.models.FloorCharacter) -> Image.Image:
    """Draw the character portrait, including the background frame"""
    background = Image.open(f"data/image/character/hsr_{character.rarity}star_bg.png").convert(
        "RGBA"
    )
    avatar_file = Path(f"data/image/character/{character.id}.png")
    # Download avatar if not exists
    if avatar_file.exists() is False:
        async with aiohttp.ClientSession() as session:
            async with session.get(character.icon) as response:
                if response.status == 200:
                    avatar_file.write_bytes(await response.read())

    avatar = Image.open(avatar_file).convert("RGBA")
    background.paste(avatar, (0, -8), avatar)
    draw_text(
        background,
        (background.width / 2, 193),
        f"{character.rank}soul {character.level}class",
        "SourceHanSansTC-Regular.otf",
        24,
        (50, 50, 50),
        "mm",
    )
    return background


async def draw_floor(
    floor: genshin.models.StarRailFloor | genshin.models.FictionFloor,
) -> Image.Image:
    """Painting the Garden of Oblivion, Fictional Narrative Floor"""
    # Create a transparent image
    img = Image.new("RGBA", (1714, 270), (0, 0, 0, 0))

    # Draw floor title
    draw_text(img, (0, 5), f"{floor.name}", "SourceHanSansTC-Bold.otf", 36, (200, 200, 200), "lt")
    draw_text(
        img,
        (img.width, 5),
        f"Use wheel：{floor.round_num}",
        "SourceHanSansTC-Regular.otf",
        32,
        (200, 200, 200),
        "rt",
    )
    # Fictional narrative has more points up and down
    if isinstance(floor, genshin.models.FictionFloor):
        draw_text(
            img,
            (1000, 5),
            f"Total score：{floor.score} ({floor.node_1.score} + {floor.node_2.score})",
            "SourceHanSansTC-Regular.otf",
            32,
            (200, 200, 200),
            "lt",
        )

    # Draw floor characters
    character_width = 156
    pad = 15
    character_num = len(floor.node_1.avatars)
    x = int(357 - character_num / 2 * character_width - (character_num - 1) * pad)
    for i, character in enumerate(floor.node_1.avatars):
        character_img = await draw_character(character)
        img.paste(character_img, (x + (character_img.width + 2 * pad) * i, 60), character_img)

    character_num = len(floor.node_2.avatars)
    x = int(1357 - character_num / 2 * character_width - (character_num - 1) * pad)
    for i, character in enumerate(floor.node_2.avatars):
        character_img = await draw_character(character)
        img.paste(character_img, (x + (character_img.width + 2 * pad) * i, 60), character_img)

    # Draw star
    star = Image.open("data/image/forgotten_hall/star.png").convert("RGBA")
    number = floor.star_num
    pos: tuple[int, int] = (int(img.width / 2), 130)
    pos = (int(pos[0] - number / 2 * (star.width) - (number - 1) * 5), pos[1])
    for i in range(number):
        img.paste(star, pos, star)
        pos = (pos[0] + star.width + 10, pos[1])
    return img


async def draw_starrail_forgottenhall_card(
    avatar_bytes: bytes,
    nickname: str,
    uid: int,
    hall: genshin.models.StarRailChallenge | genshin.models.StarRailPureFiction,
    floors: list[genshin.models.StarRailFloor] | list[genshin.models.FictionFloor],
) -> BytesIO:
    """Drawing the Garden of Oblivion, Fictional Narrative Cards"""
    MAX_FLOOR_NUM = 3
    floors = floors[:MAX_FLOOR_NUM]

    if isinstance(hall, genshin.models.StarRailChallenge):
        background_img_path = "data/image/forgotten_hall/bg.png"
        title = "The Garden of Oblivion"
    elif isinstance(hall, genshin.models.StarRailPureFiction):
        background_img_path = "data/image/forgotten_hall/bg_blue.png"
        title = "Fictional Narrative"

    img = Image.open(background_img_path).convert("RGBA")

    avatar: Image.Image = Image.open(BytesIO(avatar_bytes)).resize((160, 160), Image.LANCZOS)
    draw_avatar(img, avatar, (230, 55))

    draw_text(
        img,
        (img.width / 2, 80),
        f"{nickname} {title}",
        "SourceHanSansTC-Bold.otf",
        38,
        (255, 198, 118),
        "mm",
    )
    draw_text(
        img,
        (img.width / 2, 140),
        f"{hall.begin_time.datetime.strftime('%Y.%m.%d')} ~ {hall.end_time.datetime.strftime('%Y.%m.%d')}",
        "SourceHanSansTC-Regular.otf",
        28,
        (220, 220, 220),
        "mm",
    )
    draw_text(
        img,
        (img.width / 2, 190),
        f"Level Progress：{hall.max_floor}　Number of battles：{hall.total_battles}",
        "SourceHanSansTC-Regular.otf",
        28,
        (220, 220, 220),
        "mm",
    )
    draw_text(
        img,
        (img.width - 220, 140),
        f"★：{hall.total_stars}",
        "SourceHanSansTC-Bold.otf",
        38,
        (255, 198, 118),
        "rm",
    )
    draw_text(
        img,
        (img.width - 220, 190),
        f"UID：{uid}",
        "SourceHanSansTC-Regular.otf",
        28,
        (200, 200, 200),
        "rm",
    )

    # Draw all floors
    floor_img_height = 0
    for i, floor in enumerate(floors):
        floor_img = await draw_floor(floor)
        w = floor_img.width
        h = floor_img.height
        floor_img = floor_img.resize((int(w * 0.85), int(h * 0.85)), Image.LANCZOS)
        img.paste(
            floor_img,
            (int(img.width / 2 - floor_img.width / 2), 240 + (floor_img.height + 35) * i),
            floor_img,
        )
        floor_img_height = floor_img.height + 35

    # 裁掉多餘的部分
    img = img.crop(
        (0, 0, img.width, img.height - (MAX_FLOOR_NUM - len(floors)) * floor_img_height)
    )

    img = img.convert("RGB")
    fp = BytesIO()
    img.save(fp, "jpeg", optimize=True, quality=95)
    return fp
