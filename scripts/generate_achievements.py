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
                    desc=desc,
                    hide_desc=hidden_desc,
                    ps_desc=playstation_desc,
                    hide=hide_achievement,
                )

            save_config("achievements", achieve_data, lang=language)

if __name__ == "__main__":
    lang_assets = load_all_languages()
    SRIndexAchivements(lang_assets=lang_assets).generate()
