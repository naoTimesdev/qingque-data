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

__all__ = ("SRIndexCharacterPromotion",)


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
                        materials.append(AvatarIDNum(
                            id=str(mat["ItemID"]),
                            num=mat["ItemNum"],
                        ))
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
                    skill_up.append(AvatarIDNum(
                        id=key,
                        num=count,
                    ))
                materials = []
                for material in value["UnlockCost"]:
                    materials.append(AvatarIDNum(
                        id=str(material["ItemID"]),
                        num=material["ItemNum"],
                    ))

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


if __name__ == "__main__":
    lang_assets = load_all_languages()
    SRIndexCharacterPromotion(lang_assets=lang_assets).generate()
    SRIndexCharacterRank(lang_assets=lang_assets).generate()
