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
    remap_icon_or_image,
    save_config,
)
from sr_unity import strip_unity_rich_text

__all__ = ("SRIndexInventoryItems",)


@dataclass
class ItemData:
    id: str
    name: str
    type: str
    sub_type: str
    rarity: int
    desc: str
    story_desc: str
    icon: str
    come_from: list[str]


class SRIndexInventoryItems(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def _map_rarity(self, rarity: str) -> int:
        maps = {
            "Normal": 1,
            "NotNormal": 2,
            "Rare": 3,
            "VeryRare": 4,
            "SuperRare": 5,
        }
        return maps[rarity]

    def _generate_come_from(self, come_from_raw: dict[str, Any] | None, *, lang: str) -> list[str]:
        if come_from_raw is None:
            return []
        comes_from = []
        for value in come_from_raw.values():
            comes_from.append(
                get_hash_content(
                    value["Desc"],
                    language=lang,
                    lang_assets=self._lang_assets,
                )
            )
        return comes_from

    def _handle_icon_path(self, item_id: str, path: str, sub_type: str):
        if "Testmaterial" in path:
            # Get last part
            path = path.split("/")[-1]
            return f"icon/item/{path}"

        DEFAULT = f"icon/item/{item_id}.png"

        if path.startswith("SpriteOutput/ItemIcon"):
            # Strip the first part
            path = path.split("/")[-1]
            if path.endswith(".png"):
                path = path[:-4]
            if path.startswith("IconRelic"):
                return DEFAULT
            return f"icon/item/{path}.png"
        if path.startswith("SpriteOutput/Quest/AetherDivide/"):
            return remap_icon_or_image(path)

        return DEFAULT

    def _should_ignore_subtype(self, sub_type: str) -> bool:
        disallowed = ["ChessRogueDiceSurface", "MuseumStuff", "TravelBrochurePaster"]
        return sub_type in disallowed

    def _should_skip_item_id(self, item_id: str) -> bool:
        dis_range = range(149997, 150004 + 1)
        disallowed = [str(i) for i in dis_range] + ["149990"]
        return item_id in disallowed

    def generate(self) -> None:
        raw_items_data = read_config("ItemConfig")
        raw_items_come_from = read_config("ItemComeFrom")

        for language in get_available_languages():
            items_data = {}
            for key, value in raw_items_data.items():
                if self._should_skip_item_id(key):
                    continue

                name = get_hash_content(
                    value["ItemName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                desc = get_hash_content(
                    value["ItemDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )
                story_desc = get_hash_content(
                    value["ItemBGDesc"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                if self._should_ignore_subtype(value["ItemSubType"]):
                    continue

                items_data[key] = ItemData(
                    id=key,
                    name=name,
                    type=value["ItemMainType"],
                    sub_type=value["ItemSubType"],
                    rarity=self._map_rarity(value["Rarity"]),
                    desc=strip_unity_rich_text(desc, only_tags=["unbreak"]),
                    story_desc=strip_unity_rich_text(story_desc, only_tags=["unbreak"]),
                    icon=self._handle_icon_path(key, value["ItemIconPath"], value["ItemSubType"]),
                    come_from=self._generate_come_from(raw_items_come_from.get(key), lang=language),
                )

            print("Saving", len(items_data), "items for language", language, "...")

            save_config("items", items_data, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating items...")
    SRIndexInventoryItems(lang_assets=lang_assets).generate()
