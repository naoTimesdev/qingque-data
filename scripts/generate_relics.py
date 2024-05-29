from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sr_common import (
    LangAssets,
    SRIndexGenerator,
    get_available_languages,
    get_hash_content,
    load_all_languages,
    read_config,
    save_config,
)
from sr_unity import strip_unity_rich_text

__all__ = ("SRIndexRelics",)


@dataclass
class RelicPropData:
    type: str  # IceAddedRatio, etc
    value: float


@dataclass
class RelicData:
    id: str
    set_id: str
    name: str
    rarity: int
    type: str
    max_level: int
    main_affix_id: str
    sub_affix_id: str
    icon: str


@dataclass
class RelicSetData:
    id: str
    name: str
    desc: list[str]
    properties: list[list[RelicPropData]]
    icon: str


@dataclass
class RelicAffixPropertyData:
    affix_id: str
    property: str
    base: float
    step: float


@dataclass
class RelicSubAffixPropertyData(RelicAffixPropertyData):
    step_num: float


@dataclass
class RelicAffixData:
    id: str
    affixes: dict[str, RelicAffixPropertyData]


@dataclass
class RelicSubAffixData:
    id: str
    affixes: dict[str, RelicSubAffixPropertyData]


class SRIndexRelics(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def _do_relic_icon(self, set_id: str | int, type: str):
        type_to_num = {
            "HEAD": 0,
            "HAND": 1,
            "BODY": 2,
            "FOOT": 3,
            "NECK": 0,
            "OBJECT": 1,
        }
        return f"icon/relic/{set_id}_{type_to_num[type]}.png"

    def generate(self) -> None:
        raw_relics_data = read_config("RelicConfig")
        raw_relics_data_data = read_config("RelicDataInfo")

        for language in get_available_languages():
            relics_data = {}
            for key, value in raw_relics_data.items():
                relic_info = raw_relics_data_data[str(value["SetID"])][value["Type"]]

                name = get_hash_content(
                    relic_info["RelicName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                relics_data[key] = RelicData(
                    id=key,
                    set_id=str(value["SetID"]),
                    name=name,
                    rarity=int(value["Rarity"].replace("CombatPowerRelicRarity", "")),
                    type=value["Type"],
                    max_level=value["MaxLevel"],
                    main_affix_id=str(value["MainAffixGroup"]),
                    sub_affix_id=str(value["SubAffixGroup"]),
                    icon=self._do_relic_icon(value["SetID"], value["Type"]),
                )

            save_config("relics", relics_data, lang=language)


class SRIndexRelicSets(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def _find_prop_name(self, relic_data: dict[str, Any]) -> tuple[str, str]:
        item_101_2_props = relic_data["101"]["2"]["PropertyList"][0]

        relic_prop_name = None
        relic_prop_value = None
        for key, value in item_101_2_props.items():
            if isinstance(value, dict) and "Value" in value and relic_prop_value is None:
                relic_prop_value = key
            if isinstance(value, str) and relic_prop_name is None:
                relic_prop_name = key

        if relic_prop_name is None or relic_prop_value is None:
            raise ValueError("Failed to find relic prop name and value")
        return relic_prop_name, relic_prop_value

    def generate(self) -> None:
        raw_relics_data = read_config("RelicSetConfig")
        raw_relic_skills_data = read_config("RelicSetSkillConfig")

        rprop_name, rprop_value = self._find_prop_name(raw_relic_skills_data)

        for language in get_available_languages():
            relics_data = {}
            for key, value in raw_relics_data.items():
                name = get_hash_content(
                    value["SetName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                relic_skill = raw_relic_skills_data[key]

                desc_flatten = []
                properties_flatten = []
                for skill in relic_skill.values():
                    desc_flatten.append(
                        strip_unity_rich_text(
                            get_hash_content(
                                skill["SkillDesc"],
                                language=language,
                                lang_assets=self._lang_assets,
                            ),
                            only_tags=["unbreak"],
                        )
                    )
                    properties_flatten.append(
                        [
                            RelicPropData(
                                type=prop[rprop_name],
                                value=round(prop[rprop_value]["Value"], 3),
                            )
                            for prop in skill["PropertyList"]
                        ]
                    )

                relics_data[key] = RelicSetData(
                    id=key,
                    name=name,
                    desc=desc_flatten,
                    properties=properties_flatten,
                    icon=f"icon/relic/{key}.png",
                )

            save_config("relic_sets", relics_data, lang=language)


class SRIndexRelicMainStats(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_relics_data = read_config("RelicMainAffixConfig")

        for language in get_available_languages():
            relics_data = {}
            for key, value in raw_relics_data.items():
                affix_data = {}
                for kaffix, vaffix in value.items():
                    affix_data[kaffix] = RelicAffixPropertyData(
                        affix_id=str(vaffix["AffixID"]),
                        property=vaffix["Property"],
                        base=vaffix["BaseValue"]["Value"],
                        step=vaffix["LevelAdd"]["Value"],
                    )

                relics_data[key] = RelicAffixData(
                    id=key,
                    affixes=affix_data,
                )

            save_config("relic_main_affixes", relics_data, lang=language)


class SRIndexRelicSubStats(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_relics_data = read_config("RelicSubAffixConfig")

        for language in get_available_languages():
            relics_data = {}
            for key, value in raw_relics_data.items():
                affix_data = {}
                for kaffix, vaffix in value.items():
                    affix_data[kaffix] = RelicSubAffixPropertyData(
                        affix_id=str(vaffix["AffixID"]),
                        property=vaffix["Property"],
                        base=vaffix["BaseValue"]["Value"],
                        step=vaffix["StepValue"]["Value"],
                        step_num=vaffix["StepNum"],
                    )

                relics_data[key] = RelicSubAffixData(
                    id=key,
                    affixes=affix_data,
                )

            save_config("relic_sub_affixes", relics_data, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating relics...")
    SRIndexRelics(lang_assets=lang_assets).generate()
    print(" Generating sets...")
    SRIndexRelicSets(lang_assets=lang_assets).generate()
    print(" Generating main stats groups...")
    SRIndexRelicMainStats(lang_assets=lang_assets).generate()
    print(" Generating sub stats groups...")
    SRIndexRelicSubStats(lang_assets=lang_assets).generate()
