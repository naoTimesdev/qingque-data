from __future__ import annotations

from dataclasses import dataclass

from sr_common import (
    LangAssets,
    SRIndexGenerator,
    get_available_languages,
    get_hash_content,
    load_all_languages,
    read_config,
    remap_element_name,
    remap_icon_or_image,
    remap_path_name,
    save_config,
)
from sr_unity import strip_unity_rich_text

__all__ = ("SRIndexElements",)


@dataclass
class ElementData:
    id: str
    name: str
    desc: str
    color: str
    icon: str


@dataclass
class PathData:
    id: str
    text: str
    name: str
    desc: str
    icon: str


@dataclass
class PropertyData:
    type: str
    name: str
    field: str
    affix: bool
    ratio: bool
    percent: bool
    order: int
    icon: str


class SRIndexElements(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_data = read_config("DamageType")

        for language in get_available_languages():
            parsed_data = {}
            for key, value in raw_data.items():
                title = get_hash_content(
                    value["DamageTypeName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value["DamageTypeIntro"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                elem_data = ElementData(
                    id=key,
                    name=title,
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    color=value["Color"],
                    icon=f"icon/element/{remap_element_name(key)}.png",
                )
                parsed_data[remap_element_name(key)] = elem_data
                if key == "Thunder":
                    parsed_data[key] = elem_data

            save_config("elements", parsed_data, lang=language)


class SRIndexPaths(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_data = read_config("AvatarBaseType")

        for language in get_available_languages():
            parsed_data = {}
            for key, value in raw_data.items():
                title = get_hash_content(
                    value["BaseTypeText"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value["BaseTypeDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                icon_path = f"icon/path/{remap_path_name(key)}.png"
                if key == "Unknown":
                    icon_path = "icon/path/None.png"
                parsed_data[key] = PathData(
                    id=key,
                    text=value["FirstWordText"],
                    name=title,
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    icon=icon_path,
                )

            save_config("paths", parsed_data, lang=language)


class SRIndexProperties(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def generate(self) -> None:
        raw_data = read_config("AvatarPropertyConfig")

        for language in get_available_languages():
            parsed_data = {}
            for key, value in raw_data.items():
                title = get_hash_content(
                    value["PropertyName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                is_ratio = key.endswith("Ratio")
                is_percent = "PropertyClassify" in value and value["PropertyClassify"] == 2
                is_affix = "SubRelicFilter" in value
                parsed_data[key] = PropertyData(
                    type=value["PropertyType"],
                    name=title,
                    field="",
                    affix=is_affix,
                    ratio=is_ratio,
                    percent=is_percent,
                    order=value["Order"],
                    icon=remap_icon_or_image(value["IconPath"]),
                )

            save_config("properties.json", parsed_data, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating elements...")
    SRIndexElements(lang_assets=lang_assets).generate()
    print("Generating paths...")
    SRIndexPaths(lang_assets=lang_assets).generate()
    print("Generating properties...")
    SRIndexProperties(lang_assets=lang_assets).generate()
