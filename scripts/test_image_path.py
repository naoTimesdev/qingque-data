from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson
from sr_common import ROOT_DIR

INDEX_DIR = ROOT_DIR / "index" / "en"


def read_json(path: Path) -> dict[str, Any]:
    with path.open("rb") as fp:
        return orjson.loads(fp.read())


def process_avatars():
    print("Processing avatars...")
    avatars = INDEX_DIR / "avatars.json"
    avatars_data = read_json(avatars)

    for avatar in avatars_data.values():
        assets_path = ROOT_DIR / str(avatar["icon"])
        if not assets_path.exists():
            print(f" Missing {assets_path}")


def process_character_ranks():
    print(" Processing character ranks/eidolons...")
    chara_path = INDEX_DIR / "character_ranks.json"
    chara_data = read_json(chara_path)

    for chara in chara_data.values():
        assets_path = ROOT_DIR / str(chara["icon"])
        if not assets_path.exists():
            print(f"  Missing {assets_path}")


def process_character_skills():
    print(" Processing character skills...")
    chara_path = INDEX_DIR / "character_skills.json"
    chara_data = read_json(chara_path)

    for chara in chara_data.values():
        assets_path = ROOT_DIR / str(chara["icon"])
        if not assets_path.exists():
            print(f"  Missing {assets_path}")


def process_characters():
    print("Processing characters...")
    chara_path = INDEX_DIR / "characters.json"
    chara_data = read_json(chara_path)

    for chara in chara_data.values():
        icon_path = ROOT_DIR / str(chara["icon"])
        preview_path = ROOT_DIR / str(chara["preview"])
        portrait_path = ROOT_DIR / str(chara["portrait"])
        if not icon_path.exists():
            print(f" Missing {icon_path}")
        if not preview_path.exists():
            print(f" Missing {preview_path}")
        if not portrait_path.exists():
            print(f" Missing {portrait_path}")

    process_character_skills()
    process_character_ranks()


def process_inventory_items():
    print("Processing items...")
    chara_path = INDEX_DIR / "items.json"
    chara_data = read_json(chara_path)

    for chara in chara_data.values():
        icon_path = ROOT_DIR / str(chara["icon"])
        if not icon_path.exists():
            print(f" Missing {icon_path}")


def process_light_cones():
    print("Processing light cones...")
    lc_path = INDEX_DIR / "light_cones.json"
    lc_data = read_json(lc_path)

    for chara in lc_data.values():
        icon_path = ROOT_DIR / str(chara["icon"])
        preview_path = ROOT_DIR / str(chara["preview"])
        portrait_path = ROOT_DIR / str(chara["portrait"])
        if not icon_path.exists():
            print(f" Missing {icon_path}")
        if not preview_path.exists():
            print(f" Missing {preview_path}")
        if not portrait_path.exists():
            print(f" Missing {portrait_path}")


def process_rogue_blessings():
    print(" Processing rogue blessings...")
    simu_path = INDEX_DIR / "rogue_blessings.json"
    simu_data = read_json(simu_path)

    for simu in simu_data.values():
        icon_path = ROOT_DIR / str(simu["icon"])
        if not icon_path.exists():
            print(f"  Missing {icon_path}")


def process_rogue_curios():
    print(" Processing rogue curios...")
    simu_path = INDEX_DIR / "rogue_curios.json"
    simu_data = read_json(simu_path)

    for simu in simu_data.values():
        icon_path = ROOT_DIR / str(simu["icon"])
        if not icon_path.exists():
            print(f"  Missing {icon_path}")


def process_rogues():
    print("Processing rogues...")
    simu_path = INDEX_DIR / "rogue.json"
    simu_data = read_json(simu_path)

    for simu in simu_data.values():
        icon_path = ROOT_DIR / str(simu["icon"])
        if not icon_path.exists():
            print(f"  Missing {icon_path}")

    process_rogue_blessings()
    process_rogue_curios()


def main():
    process_avatars()
    process_characters()
    process_inventory_items()
    process_light_cones()
    process_rogues()


if __name__ == "__main__":
    main()
