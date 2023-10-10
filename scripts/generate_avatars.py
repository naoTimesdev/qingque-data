from __future__ import annotations

from dataclasses import dataclass

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

__all__ = ("SRIndexAvatars",)


@dataclass
class AvatarData:
    id: str
    name: str
    icon: str


class SRIndexAvatars(SRIndexGenerator):
    def __init__(self, *, lang_assets: LangAssets) -> None:
        self._lang_assets = lang_assets

    def _append_trailblazer(self, avatar_icon: dict[str, AvatarData]) -> None:
        missing_keys: list[str] = []
        all_keys: list[str] = ["8000", "8001", "8002", "8003", "8004"]
        for key in all_keys:
            if key not in avatar_icon:
                missing_keys.append(key)

        for key in missing_keys:
            avatar_icon[key] = AvatarData(
                id=key,
                name="{NICKNAME}",
                icon=f"icon/avatar/{key}.png",
            )

    def generate(self) -> None:
        raw_avatar_player_icon = read_config("ItemConfigAvatarPlayerIcon")
        raw_msg_contacts = read_config("MessageContactsConfig")

        for language in get_available_languages():
            avatar_icon = {}

            for key, value in raw_msg_contacts.items():
                name = get_hash_content(
                    value["Name"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                avatar_icon[key] = AvatarData(
                    id=key,
                    name=name,
                    icon=remap_icon_or_image(value["IconPath"]),
                )
            self._append_trailblazer(avatar_icon)

            for key, value in raw_avatar_player_icon.items():
                name = get_hash_content(
                    value["ItemName"],
                    language=language,
                    lang_assets=self._lang_assets,
                )

                avatar_icon[key] = AvatarData(
                    id=key,
                    name=name,
                    icon=remap_icon_or_image(value["ItemIconPath"]),
                )

            save_config("avatars", avatar_icon, lang=language)


if __name__ == "__main__":
    print("Loading language assets...")
    lang_assets = load_all_languages()
    print("Generating avatars...")
    SRIndexAvatars(lang_assets=lang_assets).generate()
