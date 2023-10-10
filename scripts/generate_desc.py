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

__all__ = ("SRIndexDescription",)


@dataclass
class LoadingDescData:
    id: str
    title: str
    desc: str


class SRIndexDescription(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_achieve_data = read_config("LoadingDesc")

        for language in get_available_languages():
            desc_load_data = {}
            for key, value in raw_achieve_data.items():
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


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating descriptions...")
    SRIndexDescription(lang_assets=lang_assets).generate()
