import typing
from pathlib import Path

from pydantic import BaseModel


class Notes(BaseModel):
    resin: str = "<:Resin:1189500526883254292>"
    realm_currency: str = "<:Realm_currency:1189500521321611294>"
    commission: str = "<:Commission:1189500524924518421>"
    enemies_of_note: str = ""
    transformer: str = "<:Transformer:1189500518041649194>"
    expedition: str = "<:Expedition:1393969298539675859>"


class Items(BaseModel):
    mora: str = "<:Mora:1189627616794267759>"
    primogem: str = "<:Primogem:1189627673371230341>"
    intertwined_fate: str = "<:IntertwinedFate:1189627731424595978>"


class Emoji(BaseModel):
    notes: Notes = Notes()
    items: Items = Items()
    elements: typing.Dict[str, str] = {}
    fightprop: typing.Dict[str, str] = {}
    artifact_type: typing.Dict[str, str] = {}
    tcg_dice_cost_elements: typing.Dict[str, str] = {}
    starrail_elements: typing.Dict[str, str] = {}


path = Path("data/emoji.json")
emoji = Emoji.parse_file(path) if path.exists() else Emoji()
