from __future__ import annotations

import importlib
from pathlib import Path
from typing import cast

from sr_common import ROOT_DIR, LangAssets, SRIndexGenerator, load_all_languages

SCRIPTS_DIR = ROOT_DIR / "scripts"


def get_all_scripts() -> list[Path]:
    return [script for script in SCRIPTS_DIR.glob("generate_*.py") if not script.stem.endswith("all")]


def get_script_generators(script: Path) -> list[type[SRIndexGenerator]]:
    mod_spec = importlib.import_module(script.stem)

    generators: list[type[SRIndexGenerator]] = []
    for name, obj in mod_spec.__dict__.items():
        # Check if inherit from SRIndexGenerator
        if isinstance(obj, SRIndexGenerator) and obj != SRIndexGenerator:
            print(f"{script.stem}: Found {name}")
            generators.append(cast(type[SRIndexGenerator], obj))

    return generators


def execute_script_generators(generators: list[type[SRIndexGenerator]], *, lang_assets: LangAssets) -> None:
    for gen_cls in generators:
        generator = gen_cls(lang_assets=lang_assets)
        print(f"Executing {gen_cls.__name__}")
        generator.generate()


def main():
    lang_data = load_all_languages()
    scripts = get_all_scripts()
    for script in scripts:
        generators = get_script_generators(script)
        execute_script_generators(generators, lang_assets=lang_data)


if __name__ == "__main__":
    main()
