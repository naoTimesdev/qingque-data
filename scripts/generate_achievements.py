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

__all__ = ("SRIndexAchivements",)


@dataclass
class AchievementData:
    id: str
    series_id: str
    title: str
    desc: str
    hide_desc: str
    ps_desc: str
    hide: bool


class SRIndexAchivements(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_achieve_data = read_config("AchievementData")

        for language in get_available_languages():
            achieve_data = {}
            for key, value in raw_achieve_data.items():
                name = get_hash_content(
                    value["AchievementTitle"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value["AchievementDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                hidden_desc = get_hash_content(
                    value["HideAchievementDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                playstation_desc = get_hash_content(
                    value["AchievementDescPS"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                hide_achievement = "ShowType" in value and value["ShowType"] == "ShowAfterFinish"
                achieve_data[key] = AchievementData(
                    id=key,
                    series_id=str(value["SeriesID"]),
                    title=name,
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    hide_desc=strip_unity_rich_text(hidden_desc, only_tags=["unbreak"]),
                    ps_desc=strip_unity_rich_text(playstation_desc, only_tags=["unbreak"]),
                    hide=hide_achievement,
                )

            save_config("achievements", achieve_data, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating achievements...")
    SRIndexAchivements(lang_assets=lang_assets).generate()
