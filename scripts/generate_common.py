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
    "SRIndexDescription",
    "SRIndexNickname",
)


@dataclass
class LoadingDescData:
    id: str
    title: str
    desc: str


class SRIndexDescription(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_desc_data = read_config("LoadingDesc")

        for language in get_available_languages():
            desc_load_data = {}
            for key, value in raw_desc_data.items():
                title = get_hash_content(
                    value["TitleTextmapID"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value["DescTextmapID"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc_load_data[key] = LoadingDescData(
                    id=key,
                    title=title,
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                )

            save_config("descriptions", desc_load_data, lang=language)


class SRIndexNickname(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_avatar_data = read_config("AvatarConfig")
        raw_weapon_data = read_config("EquipmentConfig")
        raw_relics_data = read_config("RelicSetConfig")

        for language in get_available_languages():
            avatar_nick = {}
            for key, value in raw_avatar_data.items():
                name = get_hash_content(
                    value["AvatarName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                avatar_nick[key] = [name]
            weapon_nick = {}
            for key, value in raw_weapon_data.items():
                name = get_hash_content(
                    value["EquipmentName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                weapon_nick[key] = [name]
            relic_sets_nick = {}
            for key, value in raw_relics_data.items():
                name = get_hash_content(
                    value["SetName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                relic_sets_nick[key] = [name]

            save_config(
                "nickname",
                {
                    "characters": avatar_nick,
                    "light_cones": weapon_nick,
                    "relic_sets": relic_sets_nick,
                },
                lang=language,
            )


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating descriptions...")
    SRIndexDescription(lang_assets=lang_assets).generate()
    print("Generating nicknames...")
    SRIndexNickname(lang_assets=lang_assets).generate()
