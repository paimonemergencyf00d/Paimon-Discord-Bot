import io
import json
from typing import Tuple

import discord
from cachetools import LRUCache
from honkairail.src.tools.modalV2 import StarRailApiDataV2
from hsrcard.hsr import HonkaiCard
from mihomo import MihomoAPI, StarrailInfoParsed
from mihomo import tools as mihomo_tools
from PIL.Image import Image

from database import Database, StarrailShowcase


class Showcase:
    """Honkai: Star Railway Character Display Cabinet"""

    def __init__(self, uid: int) -> None:
        self.uid = uid
        self.client = MihomoAPI()
        self.data: StarrailInfoParsed
        self.image_cache: LRUCache[int, Image] = LRUCache(maxsize=10)
        self.is_cached_data: bool = False

    async def load_data(self) -> None:
        """Get the player's character display cabinet information"""

        # Get old data from the database as cache data
        srshowcase = await Database.select_one(
            StarrailShowcase, StarrailShowcase.uid.is_(self.uid)
        )
        cached_data: StarrailInfoParsed | None = None
        if srshowcase:
            cached_data = srshowcase.data
        try:
            new_data = await self.client.fetch_user(self.uid)
        except Exception as e:
            # If the data cannot be obtained from the API, the database data is used instead. If neither is available, an error is thrown.
            if cached_data is None:
                raise e from e
            else:
                self.data = cached_data
                self.is_cached_data = True
        else:
            if cached_data is not None:
                new_data = mihomo_tools.merge_character_data(new_data, cached_data)
            self.data = mihomo_tools.remove_duplicate_character(new_data)
            await Database.insert_or_replace(StarrailShowcase(self.uid, self.data))

    def get_player_overview_embed(self) -> discord.Embed:
        """Get the embedded information of the player's basic information"""

        player = self.data.player

        description = (
            f"「{player.signature}」\n"
            f"Exploration level: {player.level}\n"
            f"Encounter characters: {player.characters}\n"
            f"Achievements: {player.achievements}\n"
        )

        if self.is_cached_data is True:
            description += "(Unable to connect to API at the moment, only cached data is displayed)\n"

        embed = discord.Embed(title=player.name, description=description)
        embed.set_thumbnail(url=self.client.get_icon_url(player.avatar.icon))

        if len(self.data.characters) > 0:
            icon = self.data.characters[0].portrait
            embed.set_image(url=self.client.get_icon_url(icon))

        embed.set_footer(text=f"UID：{player.uid}")

        return embed

    async def get_character_card_embed_file(
        self, index: int
    ) -> Tuple[discord.Embed, discord.File]:
        """Get the character's card information"""

        embed = self.get_default_embed(index)
        embed.set_thumbnail(url=None)

        if self.image_cache.get(index) is not None:
            image = self.image_cache.get(index)
        else:
            data_dict = self.data.dict(by_alias=True)
            data_dict["player"]["space_info"] = {}
            data_hsrcard = StarRailApiDataV2.parse_raw(json.dumps(data_dict, ensure_ascii=False))

            async with HonkaiCard(lang="cht") as card_creater:
                result = await card_creater.creat(self.uid, data_hsrcard, index)
                image = result.card[0].card
            self.image_cache[index] = image

        fp = io.BytesIO()
        image = image.convert("RGB")
        image.save(fp, "jpeg", optimize=True, quality=90)
        fp.seek(0)

        embed.set_image(url="attachment://image.jpeg")
        file = discord.File(fp, "image.jpeg")
        return (embed, file)

    def get_character_stat_embed(self, index: int) -> discord.Embed:
        """Get the embedded information of the character attribute data"""

        embed = self.get_default_embed(index)
        embed.title = (embed.title + "Role Panel") if embed.title is not None else "Role Panel"

        character = self.data.characters[index]

        # Basic Information
        embed.add_field(
            name="Character Information",
            value=f"Star Soul: {character.eidolon}\n" + f" Level：Lv. {character.level}\n",
        )
        # 武器
        if character.light_cone is not None:
            light_cone = character.light_cone
            embed.add_field(
                name=f"★{light_cone.rarity} {light_cone.name}",
                value=f"Overlay: {light_cone.superimpose} level\n：Lv. {light_cone.level}",
            )
        # Skill
        traces_seen = set()  # The memory skills and memory talents of the memory destiny will be repeated type_text
        embed.add_field(
            name="Skill",
            value="\n".join(
                f"{trace.type_text}：Lv. {trace.level}"
                for trace in character.traces
                if trace.type_text != "" and trace.type_text != "Secret Technique"
                and not (trace.type_text in traces_seen or traces_seen.add(trace.type_text))
            ),
            inline=False,
        )
        # 人物屬性
        attr_dict = {
            "Health": [0.0, 0.0],
            "Attack": [0.0, 0.0],
            "Defense": [0.0, 0.0],
            "Speed": [0.0, 0.0],
            "Critical Hit Rate": [0.0, 0.0],
            "Critical Hit Damage": [0.0, 0.0],
            "Energy Recovery Efficiency": [100.0, 0.0],
        }
        for stat in character.attributes:
            if stat.name not in attr_dict:
                attr_dict[stat.name] = [0.0, 0.0]
            attr_dict[stat.name][0] += stat.value * 100 if stat.is_percent else stat.value

        for stat in character.additions:
            if stat.name not in attr_dict:
                attr_dict[stat.name] = [0.0, 0.0]
            attr_dict[stat.name][1] += stat.value * 100 if stat.is_percent else stat.value

        # Damage increase that applies the damage increase to all attributes
        if "Damage increased" in attr_dict:
            v = attr_dict["Damage increased"][0] + attr_dict["Damage increased"][1]
            del attr_dict["Damage increased"]
            for key in attr_dict:
                if "Damage increased" in key:
                    attr_dict[key][1] += v

        value = ""
        for k, v in attr_dict.items():
            value += f"{k}：{round(v[0] + v[1], 1)}\n"
        embed.add_field(name="Properties panel", value=value, inline=False)

        return embed

    def get_relic_stat_embed(self, index: int) -> discord.Embed:
        """Get the embedded information of the character's artifact data"""

        embed = self.get_default_embed(index)
        embed.title = (embed.title + "Holy Relics") if embed.title is not None else "Holy Relics"

        character = self.data.characters[index]
        if character.relics is None:
            return embed

        for relic in character.relics:
            # Main article
            name = (
                relic.main_affix.name.removesuffix("Damage increased")
                .removesuffix("efficiency")
                .removesuffix("addition")
            )
            value = f"★{relic.rarity}{name}+{relic.main_affix.displayed_value}\n"
            for prop in relic.sub_affixes:
                value += f"{prop.name}+{prop.displayed_value}\n"

            embed.add_field(name=relic.name, value=value)

        return embed

    def get_relic_score_embed(self, index: int) -> discord.Embed:
        """Get the embedded message of the character's artifact entries"""

        embed = self.get_default_embed(index)
        embed.title = (embed.title + "Number of entries") if embed.title is not None else "Number of entries"

        character = self.data.characters[index]
        relics = character.relics
        if relics is None:
            return embed

        substat_sum: dict[str, float] = {  # Sub-item number statistics
            "Attack Power": 0.0,
            "Health": 0.0,
            "Defense": 0.0,
            "Speed": 0.0,
            "Critical Hit Rate": 0.0,
            "Critical Damage": 0.0,
            "Effect Hit": 0.0,
            "Effect Resistance": 0.0,
            "Break Special Attack": 0.0,
        }
        crit_value: float = 0.0  # Double explosion points

        base_hp = float(
            next(s for s in character.attributes if s.name == "Health").value
        )  # Life Points
        base_atk = float(
            next(s for s in character.attributes if s.name == "Attack Damage").value
        )  # Attack White Value
        base_def = float(
            next(s for s in character.attributes if s.name == "Defense").value
        )  # Defense White Value

        for relic in relics:
            main = relic.main_affix
            if main.name == "Critical Hit Rate":
                crit_value += float(main.value) * 100 * 2
            if main.name == "Critical Damage":
                crit_value += float(main.value) * 100
            for prop in relic.sub_affixes:
                v = prop.displayed_value
                if v is None:
                    continue
                match prop.name:
                    case "Health":
                        p = float(v.removesuffix("%")) if v.endswith("%") else float(v) / base_hp
                        substat_sum["Health"] += p / 3.89
                    case "Attack Damage":
                        p = float(v.removesuffix("%")) if v.endswith("%") else float(v) / base_atk
                        substat_sum["Attack Damage"] += p / 3.89
                    case "Defense":
                        p = float(v.removesuffix("%")) if v.endswith("%") else float(v) / base_def
                        substat_sum["Defense"] += p / 4.86
                    case "speed":
                        substat_sum["speed"] += float(v) / 2.3
                    case "Critical Hit Rate":
                        p = float(v.removesuffix("%"))
                        crit_value += p * 2.0
                        substat_sum["Critical Hit Rate"] += p / 2.92
                    case "Critical Damage":
                        p = float(v.removesuffix("%"))
                        crit_value += p
                        substat_sum["Critical Damage"] += p / 5.83
                    case "Effect hit":
                        substat_sum["Effect hit"] += float(v.removesuffix("%")) / 3.89
                    case "Effect Resistance":
                        substat_sum["Effect Resistance"] += float(v.removesuffix("%")) / 3.89
                    case "Break Special Attack":
                        substat_sum["Break Special Attack"] += float(v.removesuffix("%")) / 5.83
        embed.add_field(
            name="Number of entries",
            value="\n".join(
                [f"{k.ljust(4, '　')}：{round(v, 1)}" for k, v in substat_sum.items() if v > 0]
            ),
        )

        # Term combination statistics
        def sum_substat(name: str, *args: str) -> str:
            total = 0.0
            for arg in args:
                total += substat_sum[arg]
            # More than (4 * number of entry types) entries will be displayed
            return f"{name.ljust(4, '　')}：{round(total, 1)}\n" if total > 4 * len(args) else ""

        embed_value = f"Double Violence {round(crit_value)} point\n"
        embed_value += sum_substat("Attack double burst", "Attack power", "Critical hit rate", "Critical hit damage")
        embed_value += sum_substat("Attack speed double burst", "Attack power", "Speed", "Critical hit rate", "Critical hit damage")
        embed_value += sum_substat("Attack life double burst", "Attack power", "Effect hit", "Critical hit rate", "Critical hit damage")
        embed_value += sum_substat("Life speed double burst", "Health", "Speed", "Critical hit rate", "Critical hit damage")
        embed_value += sum_substat("Life attack speed burst", "Health", "Attack power", "Speed", "Critical hit rate", "Critical hit damage")
        embed_value += sum_substat("Life speed resistance", "Life", "Speed", "Effect resistance")
        embed_value += sum_substat("Life defense speed", "Health", "Defense power", "Speed")
        embed_value += sum_substat("Defense speed resistance", "Defense power", "Speed", "Effect Resistance")
        embed_value += sum_substat("Speed Defense Life Resistance", "Defense", "Speed", "Effect Hit", "Effect Resistance")
        embed.add_field(name="Total entry statistics", value=embed_value)

        return embed

    def get_default_embed(self, index: int) -> discord.Embed:
        """Get the basic embedding information of the character"""

        character = self.data.characters[index]
        color = {
            "Physics": 0xC5C5C5,
            "Fire": 0xF4634E,
            "Ice": 0x72C2E6,
            "Thunder": 0xDC7CF4,
            "Wind": 0x73D4A4,
            "Quantum": 0x9590E4,
            "Imaginary": 0xF7E54B,
        }
        embed = discord.Embed(
            title=f"★{character.rarity} {character.name}",
            color=color.get(character.element.name),
        )
        embed.set_thumbnail(url=self.client.get_icon_url(character.icon))

        player = self.data.player
        embed.set_author(
            name=f"{player.name} Character showcase",
            icon_url=self.client.get_icon_url(player.avatar.icon),
        )
        embed.set_footer(text=f"{player.name}．Lv. {player.level}．UID: {player.uid}")

        return embed
