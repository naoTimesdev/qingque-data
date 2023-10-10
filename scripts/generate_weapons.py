from __future__ import annotations

from dataclasses import dataclass

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

__all__ = (
    "SRIndexLightCones",
    "SRIndexLightConePromotion",
    "SRIndexLightConeRank",
)


@dataclass
class WeaponPromoValue:
    base: float
    step: float


@dataclass
class WeaponIDNum:
    id: str
    num: int


@dataclass
class WeaponPropertyData:
    type: str  # IceAddedRatio, etc
    value: float


@dataclass
class WeaponPromoData:
    id: str
    values: list[dict[str, WeaponPromoValue]]
    materials: list[list[WeaponIDNum]]


@dataclass
class WeaponRankData:
    id: str
    skill: str
    desc: str
    params: list[list[float]]
    properties: list[list[WeaponPropertyData]]


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
class AvatarSkillTreeLevelData:
    promotion: int
    properties: list[WeaponPropertyData]
    materials: list[WeaponIDNum]


@dataclass
class AvatarSkillTreeData:
    id: str
    name: str
    max_level: int
    desc: str
    params: list[list[float]]
    anchor: str
    pre_points: list[str]  # required previous points?
    level_up_skills: list[WeaponIDNum]
    levels: list[AvatarSkillTreeLevelData]


@dataclass
class WeaponData:
    id: str
    name: str
    rarity: int
    path: str
    desc: str
    icon: str
    preview: str
    portrait: str


class SRIndexLightConePromotion(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_weapon_config = read_config("EquipmentPromotionConfig")

        for language in get_available_languages():
            weapon_config = {}

            for key, value_base in raw_weapon_config.items():
                all_promo_keys: list[dict[str, WeaponPromoValue]] = []
                materials_comp: list[list[WeaponIDNum]] = []
                for value in value_base.values():
                    materials: list[WeaponIDNum] = []
                    for mat in value["PromotionCostList"]:
                        materials.append(
                            WeaponIDNum(
                                id=str(mat["ItemID"]),
                                num=mat["ItemNum"],
                            )
                        )
                    materials_comp.append(materials)

                    promo_keys: dict[str, WeaponPromoValue] = {
                        "hp": WeaponPromoValue(
                            base=value["BaseHP"]["Value"],
                            step=round(value["BaseHPAdd"]["Value"], 2),
                        ),
                        "atk": WeaponPromoValue(
                            base=round(value["BaseAttack"]["Value"], 2),
                            step=round(value["BaseAttackAdd"]["Value"], 2),
                        ),
                        "def": WeaponPromoValue(
                            base=round(value["BaseDefence"]["Value"], 2),
                            step=round(value["BaseDefenceAdd"]["Value"], 2),
                        ),
                    }
                    all_promo_keys.append(promo_keys)
                weapon_config[key] = WeaponPromoData(
                    id=key,
                    values=all_promo_keys,
                    materials=materials_comp,
                )

            save_config("light_cone_promotions", weapon_config, lang=language)


class SRIndexLightConeRank(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_weapon_config = read_config("EquipmentSkillConfig")

        for language in get_available_languages():
            weapon_config = {}

            for _key, value in raw_weapon_config.items():
                first_val = value["1"]
                name = get_hash_content(
                    first_val["SkillName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    first_val["SkillDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                params_flatten = []
                properties_flatten = []
                for level_val in value.values():
                    params_flatten.append([round(param["Value"], 3) for param in level_val["ParamList"]])
                    prop_ads = [
                        WeaponPropertyData(type=prop["PropertyType"], value=round(prop["Value"]["Value"], 3))
                        for prop in level_val["AbilityProperty"]
                    ] or []
                    properties_flatten.append(prop_ads)

                weapon_config[_key] = WeaponRankData(
                    id=_key,
                    skill=name,
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    params=params_flatten,
                    properties=properties_flatten,
                )

            save_config("light_cone_ranks", weapon_config, lang=language)


class SRIndexLightCones(SRIndexGenerator):
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
        raw_weapon_config = read_config("EquipmentConfig")

        for language in get_available_languages():
            weapon_config = {}

            for _key, value_base in raw_weapon_config.items():
                name = get_hash_content(
                    value_base["EquipmentName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value_base["EquipmentDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                if desc != "":
                    print(f"Character {_key} ({name}) has a description, but it's not used")

                weapon_config[_key] = WeaponData(
                    id=_key,
                    name=name,
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    rarity=int(value_base["Rarity"].replace("CombatPowerLightconeRarity", "")),
                    path=value_base["AvatarBaseType"],
                    icon=f"icon/light_cone/{_key}.png",
                    preview=f"image/light_cone_preview/{_key}.png",
                    portrait=f"image/light_cone_portrait/{_key}.png",
                )

            save_config("light_cones", weapon_config, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating light cones...")
    SRIndexLightCones(lang_assets=lang_assets).generate()
    print(" Generating promotions/ascensions...")
    SRIndexLightConePromotion(lang_assets=lang_assets).generate()
    print(" Generating ranks/superimpose...")
    SRIndexLightConeRank(lang_assets=lang_assets).generate()
