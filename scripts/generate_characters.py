from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

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
    "SRIndexCharacterBase",
    "SRIndexCharacterPromotion",
    "SRIndexCharacterRank",
    "SRIndexCharacterSkills",
)


@dataclass
class AvatarPromoValue:
    base: float
    step: float


@dataclass
class AvatarIDNum:
    id: str
    num: int


@dataclass
class AvatarPromoData:
    id: str
    values: list[dict[str, AvatarPromoValue]]
    materials: list[list[AvatarIDNum]]


@dataclass
class AvatarRankData:
    id: str
    name: str
    rank: int
    desc: str
    icon: str
    materials: list[AvatarIDNum]
    level_up_skills: list[AvatarIDNum]
    icon: str


@dataclass
class AvatarSkillData:
    id: str
    name: str
    max_level: int
    element: str
    type: str
    type_text: str
    effect: str
    effect_text: str
    simple_desc: str
    desc: str
    params: list[list[float]]
    icon: str


@dataclass
class AvatarPropertyData:
    type: str  # IceAddedRatio, etc
    value: float


@dataclass
class AvatarSkillTreeLevelData:
    promotion: int
    properties: list[AvatarPropertyData]
    materials: list[AvatarIDNum]


@dataclass
class AvatarSkillTreeData:
    id: str
    name: str
    max_level: int
    desc: str
    params: list[list[float]]
    anchor: str
    pre_points: list[str]  # required previous points?
    level_up_skills: list[AvatarIDNum]
    levels: list[AvatarSkillTreeLevelData]


@dataclass
class AvatarData:
    id: str
    name: str
    tag: str
    rarity: int
    path: str
    element: str
    max_sp: int
    ranks: list[str]
    skills: list[str]
    skill_trees: list[str]
    icon: str
    preview: str
    portrait: str


class SRIndexCharacterPromotion(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_avatar_config = read_config("AvatarPromotionConfig")

        for language in get_available_languages():
            avatar_config = {}

            for key, value_base in raw_avatar_config.items():
                all_promo_keys: list[dict[str, AvatarPromoValue]] = []
                materials_comp: list[list[AvatarIDNum]] = []
                for value in value_base.values():
                    materials: list[AvatarIDNum] = []
                    for mat in value["PromotionCostList"]:
                        materials.append(
                            AvatarIDNum(
                                id=str(mat["ItemID"]),
                                num=mat["ItemNum"],
                            )
                        )
                    materials_comp.append(materials)

                    promo_keys: dict[str, AvatarPromoValue] = {
                        "hp": AvatarPromoValue(
                            base=value["HPBase"]["Value"],
                            step=round(value["HPAdd"]["Value"], 2),
                        ),
                        "atk": AvatarPromoValue(
                            base=round(value["AttackBase"]["Value"], 2),
                            step=round(value["AttackAdd"]["Value"], 2),
                        ),
                        "def": AvatarPromoValue(
                            base=round(value["DefenceBase"]["Value"], 2),
                            step=round(value["DefenceAdd"]["Value"], 2),
                        ),
                        "spd": AvatarPromoValue(
                            base=round(value["SpeedBase"]["Value"], 2),
                            step=round(value["SpeedBase"]["Value"], 2),
                        ),
                        "crit_rate": AvatarPromoValue(
                            base=round(value["CriticalChance"]["Value"], 2),
                            step=0,
                        ),
                        "crit_dmg": AvatarPromoValue(
                            base=round(value["CriticalDamage"]["Value"], 2),
                            step=0,
                        ),
                    }
                    all_promo_keys.append(promo_keys)
                avatar_config[key] = AvatarPromoData(
                    id=key,
                    values=all_promo_keys,
                    materials=materials_comp,
                )

            save_config("character_promotions", avatar_config, lang=language)


class SRIndexCharacterRank(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_avatar_config = read_config("AvatarRankConfig")

        for language in get_available_languages():
            avatar_config = {}

            for _key, value in raw_avatar_config.items():
                name = get_hash_content(
                    value["Name"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value["Desc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                skill_up = []
                for key, count in value["SkillAddLevelList"].items():
                    skill_up.append(
                        AvatarIDNum(
                            id=key,
                            num=count,
                        )
                    )
                materials = []
                for material in value["UnlockCost"]:
                    materials.append(
                        AvatarIDNum(
                            id=str(material["ItemID"]),
                            num=material["ItemNum"],
                        )
                    )

                params_flatten = []
                for params in value["Param"]:
                    params_flatten.append(params["Value"])

                avatar_config[_key] = AvatarRankData(
                    id=_key,
                    name=name,
                    rank=value["Rank"],
                    desc=strip_unity_rich_text(format_with_params(desc, params_flatten), only_tags=["unbreak"]),
                    materials=materials,
                    level_up_skills=skill_up,
                    icon=remap_icon_or_image(value["IconPath"]),
                )

            save_config("character_ranks", avatar_config, lang=language)


class SRIndexCharacterSkills(SRIndexGenerator):
    UNUSED_SKILLS_TAG: ClassVar[list[int]] = [1323314283]

    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_avatar_skill_config = read_config("AvatarSkillConfig")
        raw_avatar_skill_trees_config = read_config("AvatarSkillTreeConfig")

        for language in get_available_languages():
            avatar_skill_config = {}

            for _key, value in raw_avatar_skill_config.items():
                val_first = value["1"]
                sk_tag = val_first["SkillTag"]
                if sk_tag["Hash"] in self.UNUSED_SKILLS_TAG:
                    continue
                name = get_hash_content(
                    val_first["SkillName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    val_first["SkillDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                simple_desc = get_hash_content(
                    val_first["SimpleSkillDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                type_desc = get_hash_content(
                    val_first["SkillTypeDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                effect_desc = get_hash_content(
                    sk_tag,
                    language=language,
                    lang_assets=self._lang_assets,
                )

                params = []
                for level_val in value.values():
                    params.append([round(p_lvl["Value"], 3) for p_lvl in level_val["ParamList"]])
                if "AttackType" not in val_first:
                    val_first["AttackType"] = "Talent"
                if "StanceDamageType" not in val_first:
                    val_first["StanceDamageType"] = ""

                avatar_skill_config[_key] = AvatarSkillData(
                    id=_key,
                    name=name,
                    max_level=val_first["MaxLevel"],
                    element=val_first["StanceDamageType"],
                    type=val_first["AttackType"],
                    type_text=type_desc,
                    effect=val_first["SkillEffect"],
                    effect_text=effect_desc,
                    params=params,
                    simple_desc=strip_unity_rich_text(simple_desc, only_tags=["unbreak"]),
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    icon=remap_icon_or_image(val_first["SkillIcon"]),
                )

            save_config("character_skills", avatar_skill_config, lang=language)

            avatar_skill_tress_config = {}
            for _key, value in raw_avatar_skill_trees_config.items():
                first_val = value["1"]
                name = ""
                if first_val["PointName"] != "":
                    name = get_hash_content(
                        first_val["PointName"],
                        language=language,
                        lang_assets=self._lang_assets,
                    )
                elif first_val["AbilityName"] != "":
                    name = get_hash_content(
                        first_val["AbilityName"],
                        language=language,
                        lang_assets=self._lang_assets,
                    )

                desc = ""
                if first_val["PointDesc"] != "":
                    desc = get_hash_content(
                        first_val["PointDesc"],
                        language=language,
                        lang_assets=self._lang_assets,
                    )

                params = []
                levels_data: list[AvatarSkillTreeLevelData] = []
                for idx, level_val in enumerate(value.values()):
                    params.append([round(p_lvl["Value"], 3) for p_lvl in level_val["ParamList"]])
                    promo_properties = [
                        AvatarPropertyData(type=prop["PropertyType"], value=round(prop["Value"]["Value"], 3))
                        for prop in level_val["StatusAddList"]
                    ]
                    promo_mats = [
                        AvatarIDNum(
                            id=str(mat["ItemID"]),
                            num=mat["ItemNum"],
                        )
                        for mat in level_val["MaterialList"]
                    ]
                    levels_data.append(
                        AvatarSkillTreeLevelData(
                            promotion=idx,
                            properties=promo_properties,
                            materials=promo_mats,
                        )
                    )
                level_up_skills = []
                if "LevelUpSkillID" in first_val:
                    level_up_skills = [
                        AvatarIDNum(
                            id=str(skill_id),
                            num=1,
                        )
                        for skill_id in first_val["LevelUpSkillID"]
                    ]

                if "PrePoint" not in first_val:
                    print(f"-- Missing PrePoint for {_key} ({name})")
                    first_val["PrePoint"] = []

                avatar_skill_tress_config[_key] = AvatarSkillTreeData(
                    id=_key,
                    name=name,
                    max_level=first_val["MaxLevel"],
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    params=params,
                    anchor=first_val["Anchor"],
                    pre_points=list(map(str, first_val["PrePoint"])),
                    level_up_skills=level_up_skills,
                    levels=levels_data,
                )

            save_config("character_skill_trees", avatar_skill_tress_config, lang=language)


class SRIndexCharacterBase(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    @staticmethod
    def _get_skill_trees(chara_id: str, skill_trees: list[str]) -> list[str]:
        skill_trees_comp = []
        for skill_tree in skill_trees:
            if skill_tree.startswith(chara_id):
                skill_trees_comp.append(skill_tree)
        return skill_trees_comp

    def generate(self) -> None:
        raw_avatar_config = read_config("AvatarConfig")
        raw_avatar_trees_config = read_config("AvatarSkillTreeConfig")

        all_avatar_trees_keys = list(raw_avatar_trees_config.keys())

        for language in get_available_languages():
            avatar_config = {}

            for _key, value_base in raw_avatar_config.items():
                name = get_hash_content(
                    value_base["AvatarName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value_base["AvatarDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                if desc != "":
                    print(f"Character {_key} ({name}) has a description, but it's not used")

                avatar_config[_key] = AvatarData(
                    id=_key,
                    name=name,
                    tag=value_base["AvatarVOTag"],
                    rarity=int(value_base["Rarity"].replace("CombatPowerAvatarRarityType", "")),
                    path=value_base["AvatarBaseType"],
                    element=value_base["DamageType"],
                    max_sp=value_base["SPNeed"]["Value"],
                    ranks=list(map(str, value_base["RankIDList"])),
                    skills=list(map(str, value_base["SkillList"])),
                    skill_trees=self._get_skill_trees(_key, all_avatar_trees_keys),
                    icon=f"icon/character/{_key}.png",
                    preview=f"image/character_preview/{_key}.png",
                    portrait=f"image/character_portrait/{_key}.png",
                )

            save_config("characters", avatar_config, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating characters...")
    SRIndexCharacterBase(lang_assets=lang_assets).generate()
    print(" Generating character skills...")
    SRIndexCharacterSkills(lang_assets=lang_assets).generate()
    print(" Generating character promotions/ascensions...")
    SRIndexCharacterPromotion(lang_assets=lang_assets).generate()
    print(" Generating character ranks/eidolons...")
    SRIndexCharacterRank(lang_assets=lang_assets).generate()
