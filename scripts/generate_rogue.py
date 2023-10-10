from __future__ import annotations

from dataclasses import dataclass

from sr_common import (
    LangAssets,
    SRIndexGenerator,
    format_with_params,
    get_available_languages,
    get_hash_content,
    load_all_languages,
    read_config,
    remap_icon_or_image,
    save_config,
)
from sr_unity import strip_unity_rich_text

__all__ = (
    "SRIndexRogueWorld",
    "SRIndexRogueBlessings",
    "SRIndexRogueCurios",
)


@dataclass
class RogueBuff:
    id: int
    name: str
    icon: str
    desc: str
    simple_desc: str
    desc_battle: str
    max_level: int
    rarity: int
    kind: int
    params: list[int | float]


@dataclass
class RogueMiracle:
    id: int
    name: str
    icon: str
    desc: str
    params: list[int]
    story_desc: str
    tag: str


@dataclass
class RogueWorld:
    id: int
    """The actual ID"""
    area_id: int
    """The area progress ID (world numbering)"""
    name: str
    icon: str
    difficulty: int
    recommend_level: int
    score_map: dict[str, int]
    weakness: list[str]


@dataclass
class RogueBuffType:
    id: int
    name: str
    icon: str
    hint: str


@dataclass
class RogueBlockType:
    id: int
    name: str
    icon: str
    color: str


class SRIndexRogueBlessings(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        buff_raw_data = read_config("RogueBuff")
        buff_rogue_display_raw_data = read_config("RogueMazeBuff")
        buff_maze_display_raw_data = read_config("MazeBuff")
        buff_type_raw_data = read_config("RogueBuffType")

        for language in get_available_languages():
            parsed_buff_data = {}

            for key, value in buff_raw_data.items():
                buff_raw_level = value["1"]
                if buff_raw_level["RogueBuffType"] == 100:
                    continue
                buff_id = str(buff_raw_level["MazeBuffID"])
                first_level = buff_rogue_display_raw_data.get(
                    buff_id,
                    buff_maze_display_raw_data.get(buff_id, {}),
                )["1"]

                name = get_hash_content(
                    first_level["BuffName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    first_level["BuffDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                simple_desc = get_hash_content(
                    first_level["BuffSimpleDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                battle_desc = get_hash_content(
                    first_level["BuffDescBattle"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                params = list(map(lambda x: x["Value"], first_level["ParamList"]))

                parsed_buff_data[key] = RogueBuff(
                    id=int(buff_id),
                    name=name,
                    icon=remap_icon_or_image(first_level["BuffIcon"]),
                    desc=strip_unity_rich_text(format_with_params(desc, params), only_tags=["unbreak"]),
                    simple_desc=strip_unity_rich_text(format_with_params(simple_desc, params), only_tags=["unbreak"]),
                    desc_battle=strip_unity_rich_text(format_with_params(battle_desc, params), only_tags=["unbreak"]),
                    max_level=first_level["LvMax"],
                    params=params,
                    rarity=buff_raw_level["RogueBuffRarity"],
                    kind=buff_raw_level["RogueBuffType"],
                )

            parsed_buff_type_data = {}
            for key, value in buff_type_raw_data.items():
                buff_type_id = value["RogueBuffType"]
                if buff_type_id == 100:
                    continue

                name = get_hash_content(
                    value["RogueBuffTypeTextmapID"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                hint_desc = get_hash_content(
                    value["HintDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                parsed_buff_type_data[key] = RogueBuffType(
                    id=buff_type_id,
                    name=strip_unity_rich_text(name),
                    icon=remap_icon_or_image(value["RogueBuffTypeIcon"]),
                    hint=strip_unity_rich_text(hint_desc),
                )

            save_config("rogue_blessings", parsed_buff_data, lang=language)
            save_config("rogue_blessing_types", parsed_buff_type_data, lang=language)


class SRIndexRogueCurios(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        miracle_raw_data = read_config("RogueMiracle")
        miracle_disp_raw_data = read_config("RogueMiracleDisplay")

        for language in get_available_languages():
            parsed_curio_data = {}

            for key, value_raw in miracle_raw_data.items():
                value = miracle_disp_raw_data[str(value_raw["MiracleDisplayID"])]

                name = get_hash_content(
                    value["MiracleName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value["MiracleDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                bg_desc = get_hash_content(
                    value["MiracleBGDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                tag = get_hash_content(
                    value["MiracleTag"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                params = list(map(lambda x: x["Value"], value["DescParamList"]))

                parsed_curio_data[key] = RogueMiracle(
                    id=value_raw["MiracleID"],
                    name=name,
                    icon=remap_icon_or_image(value["MiracleIconPath"], force_initial="rogue/curios"),
                    desc=strip_unity_rich_text(format_with_params(desc, params)),
                    params=params,
                    story_desc=strip_unity_rich_text(format_with_params(bg_desc, params)),
                    tag=tag,
                )

            save_config("rogue_curios", parsed_curio_data, lang=language)


class SRIndexRogueWorld(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        world_raw_data = read_config("RogueAreaConfig")
        dlc_block_type_raw_data = read_config("RogueDLCBlockType")

        for language in get_available_languages():
            parsed_world_data = {}
            parsed_dlc_blocks_data = {}

            for key, value in world_raw_data.items():
                name = get_hash_content(
                    value["AreaNameID"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                area_progress = value.get("AreaProgress", 0)
                area_icon = f"icon/rogue/worlds/PlanetM{area_progress}.png"
                if area_progress == 0:
                    area_icon = "icon/rogue/worlds/PlanetM1.png"

                parsed_world_data[key] = RogueWorld(
                    id=value["RogueAreaID"],
                    area_id=area_progress,
                    name=strip_unity_rich_text(name),
                    icon=area_icon,
                    difficulty=value["Difficulty"],
                    recommend_level=value["RecommendLevel"],
                    score_map=value["ScoreMap"],
                    weakness=value["RecommendNature"],
                )

            boss_blocks = [11, 12]
            boss_block_col = "#8f3344ff"
            for key, value in dlc_block_type_raw_data.items():
                name = get_hash_content(
                    value["BlockTypeNameID"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                color = value["BlockTypeChessBoardColor"]
                if value["BlockTypeID"] in boss_blocks:
                    color = boss_block_col

                parsed_dlc_blocks_data[key] = RogueBlockType(
                    id=value["BlockTypeID"],
                    name=strip_unity_rich_text(name),
                    icon=remap_icon_or_image(value["BlockTypeIcon"]),
                    color=color,  # (hex with alpha)
                )

            save_config("rogue", parsed_world_data, lang=language)
            save_config("rogue_dlc_blocks", parsed_dlc_blocks_data, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating rogues/simulated universe...")
    SRIndexRogueWorld(lang_assets=lang_assets).generate()
    print(" Generating blessings...")
    SRIndexRogueBlessings(lang_assets=lang_assets).generate()
    print(" Generating curios...")
    SRIndexRogueCurios(lang_assets=lang_assets).generate()
