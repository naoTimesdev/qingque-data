from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Final, Protocol, TypeAlias, TypedDict, TypeVar, overload, runtime_checkable

import orjson

__all__ = (
    "ROOT_DIR",
    "CONFIG_DIR",
    "TEXTMAPS_DIR",
    "HASH_NO_OPTION",
    "LangAssets",
    "SRIndexGenerator",
    "format_language",
    "load_all_languages",
    "get_available_languages",
    "get_stable_hash",
    "get_hash_content",
    "remap_path_name",
    "remap_element_name",
    "remap_icon_or_image",
    "format_with_params",
    "read_config",
    "save_config",
)
ROOT_DIR = Path(__file__).absolute().parent.parent
CONFIG_DIR = ROOT_DIR / "exceloutput"
TEXTMAPS_DIR = ROOT_DIR / "textmaps"
INDEX_DIR = ROOT_DIR / "index"
HASH_NO_OPTION: Final[int] = 371857150
_TDict = TypeVar("_TDict", bound=TypedDict)  # type: ignore
_Lang: TypeAlias = str
LangAssets: TypeAlias = dict[_Lang, dict[str, str]]


class Hashable(TypedDict):
    Hash: int


@runtime_checkable
class SRIndexGenerator(Protocol):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        ...

    def generate(self) -> None:
        ...


def format_language(language_fn: str) -> str:
    la = language_fn.replace("TextMap", "").lower()
    return "cn" if la == "chs" else la


def load_all_languages(specific_lang: list[str] | None = None) -> LangAssets:
    LANGUAGES_ASSETS: LangAssets = {}
    languages = list(TEXTMAPS_DIR.glob("*.json"))

    for language in languages:
        if "TextMapMain" in language.stem:
            continue
        fmt_lang = format_language(language.stem)
        if specific_lang is not None and len(specific_lang) > 0 and fmt_lang not in specific_lang:
            continue
        with language.open("rb") as f:
            LANGUAGES_ASSETS[format_language(language.stem)] = orjson.loads(f.read())
    return LANGUAGES_ASSETS


def get_available_languages() -> list[str]:
    languages = list(TEXTMAPS_DIR.glob("*.json"))
    ALL_LANGUAGES = [format_language(language.stem) for language in languages if "TextMapMain" not in language.stem]
    return ALL_LANGUAGES


def get_stable_hash(s: int | str) -> str:
    s = str(s)
    hash1 = 5381
    hash2 = 5381

    i = 0
    while i < len(s):
        char_code = ord(s[i])
        hash1 = ((hash1 << 5) + hash1) ^ char_code
        if i + 1 < len(s):
            char_code = ord(s[i + 1])
            hash2 = ((hash2 << 5) + hash2) ^ char_code
        i += 2

    combined_hash = (hash1 + (hash2 * 1566083941)) & 0xFFFFFFFF
    combined_hash = combined_hash if combined_hash <= 0x7FFFFFFF else combined_hash - 0x100000000
    return str(combined_hash)


def get_hash_content(hash_int_str: int | str | Hashable, language: str = "en", *, lang_assets: LangAssets) -> str:
    if isinstance(hash_int_str, dict):
        hash_int_str = hash_int_str["Hash"]
    hash_str = str(hash_int_str)
    if str(HASH_NO_OPTION) == hash_str:
        return ""
    return lang_assets[language].get(
        hash_str,
        lang_assets[language].get(
            get_stable_hash(hash_str),
            "",
        ),
    )


def remap_path_name(path_name: str):
    replacer = {
        "Knight": "Preservation",
        "Pirest": "Abundance",
        "Priest": "Abundance",
        "Warrior": "Destruction",
        "Rogue": "Hunt",
        "Mage": "Erudition",
        "Shaman": "Harmony",
        "Warlock": "Nihility",
    }
    for key, value in replacer.items():
        path_name = path_name.replace(key, value)
    return path_name


def remap_skill_name(skill_name: str):
    replacer = {
        "normal02": "basic_atk",
        "normal03": "basic_atk",
        "normal04": "basic_atk",
        "normal": "basic_atk",
        "passive": "talent",
        "maze": "technique",
        "bp02": "skill",
        "bp": "skill",
        "ultra0": "ultimateS",
        "ultra": "ultimate",
    }
    for key, value in replacer.items():
        skill_name = skill_name.replace(key, value)
    return skill_name


def remap_element_name(elem_name: str):
    replacer = {
        "Thunder": "Lightning",
    }
    for key, value in replacer.items():
        elem_name = elem_name.replace(key, value)
    return elem_name


def _warn_unhandled_path(path: str):
    if path.lower().startswith("spriteoutput/"):
        print(f">> Unhandled path: {path}")


def remap_icon_or_image(path: str, *, force_initial: str | None = None, item_id: str | None = None):
    # Simulated Universe
    if path.startswith("SpriteOutput/Rogue/Buff/"):
        return path.replace("SpriteOutput/Rogue/Buff/", "icon/rogue/blessings/")
    if path.startswith("SpriteOutput/ItemIcon/"):
        if force_initial is not None:
            return path.replace("SpriteOutput/ItemIcon/", f"icon/{force_initial}/")
        return path.replace("SpriteOutput/ItemIcon/", "icon/item/")
    if path.startswith("SpriteOutput/AvatarProfessionTattoo/Profession/"):
        path = path.replace(
            "SpriteOutput/AvatarProfessionTattoo/Profession/BgPathsn", "icon/rogue/blessings/RogueIntervene"
        )
        path = path.replace(
            "SpriteOutput/AvatarProfessionTattoo/Profession/BgPaths", "icon/rogue/blessings/RogueIntervene"
        )
        return path
    if path.startswith("SpriteOutput/ProfessionIconMiddle/IconProfession"):
        path = path.replace("SpriteOutput/ProfessionIconMiddle/IconProfession", "icon/path/")
        path = path.replace("Middle", "")
        return remap_path_name(path)
    if path.startswith("SpriteOutput/Rogue/MiracleIcon/"):
        return path.replace("SpriteOutput/Rogue/MiracleIcon/", "icon/rogue/curios/")
    if path.startswith("SpriteOutput/Rogue/Map/"):
        path = path.replace("SpriteOutput/Rogue/Map/", "icon/rogue/room/")
        if "RandomIcon" in path and "RogueDlc" in path:
            path = path.replace("RandomIcon", "RandomSwarmIcon")
        if "BossIcon" in path and "RogueDlc" in path:
            path = path.replace("BossIcon", "BossSwarmIcon")
        return path.replace("/RogueDlc", "/").replace("/Rogue", "/")

    # Messages
    if path.startswith("SpriteOutput/AvatarRoundIcon/UI_Message_Contacts"):
        # Get everything after ui_message_contacts
        path = path.split("UI_Message_Contacts")[1][1:]
        return f"icon/avatar/{path}"
    if path.startswith("SpriteOutput/AvatarRoundIcon/Series/"):
        path = path.replace("SpriteOutput/AvatarRoundIcon/Series/", "icon/avatar/")
        return path
    if path.startswith("SpriteOutput/AvatarRoundIcon"):
        # Remove the first part
        path = path.split("AvatarRoundIcon")[1][1:]
        path = path.replace("UI_Message_Group_", "Group")
        if path.startswith("UI_Message_"):
            path = path.split("UI_Message_")[1]
        return f"icon/avatar/{path}"
    if path.startswith("SpriteOutput/MonsterRoundIcon/"):
        path = path.replace("SpriteOutput/MonsterRoundIcon/", "icon/avatar/")
        return path
    if path.startswith("SpriteOutput/Emoji/"):
        if path.startswith("SpriteOutput/Emoji/Mission/"):
            if item_id is not None:
                return f"icon/emoji/{item_id}.png"
            return path.replace("SpriteOutput/Emoji/Mission/", "icon/emoji/Mission")
        return path.replace("SpriteOutput/Emoji/", "icon/emoji/")
    if path.startswith("SpriteOutput/PhoneMessagePic/"):
        path = path.replace("SpriteOutput/PhoneMessagePic/PhoneMessagePic_", "image/messages/")
        return path.replace("SpriteOutput/PhoneMessagePic/PhoneMessagePic", "image/messages/E")
    if path.startswith("SpriteOutput/PhoneMessageChallenge/PhoneMessageChallenge_"):
        return path.replace("SpriteOutput/PhoneMessageChallenge/PhoneMessageChallenge_", "image/messages/Raid")
    if path.startswith("SpriteOutput/Quest/GuessTheSilhouette/"):
        return path.replace("SpriteOutput/Quest/GuessTheSilhouette/", "image/messages/March")
    if path.startswith("SpriteOutput/Quest/Heliobus/PhoneMessageHeliobus"):
        return path.replace("SpriteOutput/Quest/Heliobus/PhoneMessageHeliobus/", "image/messages/Link_")

    # Characters
    if path.startswith("SpriteOutput/SkillIcons/"):
        # Get the last part
        path = path.split("/")[-1].replace("SkillIcon_", "").lower()
        # Replacer
        path = remap_skill_name(path)
        return f"icon/skill/{path}"

    # Properties
    if path.startswith("SpriteOutput/UI/Avatar/Icon/"):
        path = path.replace("SpriteOutput/UI/Avatar/Icon/", "icon/property/")
        return path

    # Aetherium Wars
    if path.startswith("SpriteOutput/Quest/AetherDivide"):
        path = path.replace(
            "SpriteOutput/Quest/AetherDivide/AssembleSkill/Icon/IconAetherDivideAssembleSkill",
            "icon/aether/assemble_skills/AssembleSkill",
        )
        return path

    _warn_unhandled_path(path)
    return path


def _int_formatter_param(text_data: str, pos: int, param: int | float):
    i_regex = re.compile(rf"#{pos}\[i\]")
    ip_regex = re.compile(rf"#{pos}\[i\]%")
    f_regex = re.compile(rf"#{pos}\[f(\d+)\]")
    fp_regex = re.compile(rf"#{pos}\[f(\d+)\]%")

    # Check if it's int
    if ip_regex.search(text_data):
        mul_param = round(param * 100)
        return ip_regex.sub(f"{mul_param}%", text_data)
    elif i_regex.search(text_data):
        # Replace
        return i_regex.sub(str(round(param)), text_data)
    # Check if it's float
    elif (fp_res := fp_regex.search(text_data)) is not None:
        decimal_places = int(fp_res.group(1))
        mul_param = round(param * 100, decimal_places)
        return fp_regex.sub(f"{mul_param}%", text_data)
    elif (f_res := f_regex.search(text_data)) is not None:
        # Get the decimal places
        decimal_places = int(f_res.group(1))
        # Replace
        rounded_param = round(param, decimal_places)
        return f_regex.sub(f"{rounded_param}", text_data)
    return text_data


def format_with_params(text_data: str, parameters: list[int | float]) -> str:
    # Parameter like: #1[i] #2[f1] #3[f2]
    # [i] would be format as int, rounded
    # [fX] would be format as float, with X decimal places
    if not parameters:
        return text_data

    for pos, param in enumerate(parameters, 1):
        text_data = _int_formatter_param(text_data, pos, param)
    return text_data


@overload
def read_config(config_name: str) -> dict[str, Any]:
    ...


@overload
def read_config(config_name: str, *, type: None) -> dict[str, Any]:
    ...


@overload
def read_config(config_name: str, *, type: type[_TDict]) -> dict[str, _TDict]:
    ...


def read_config(config_name: str, *, type: type[_TDict] | None = None) -> dict[str, _TDict | Any]:
    if not config_name.endswith(".json"):
        config_name += ".json"
    conf_path = CONFIG_DIR / config_name
    with conf_path.open("rb") as fp:
        return orjson.loads(fp.read())


def save_config(config_name: str, data: dict[str, Any], *, lang: str, options: int | None = None):
    if not config_name.endswith(".json"):
        config_name += ".json"
    conf_path = INDEX_DIR / lang / config_name
    with conf_path.open("wb") as fp:
        fp.write(orjson.dumps(data, option=options))
