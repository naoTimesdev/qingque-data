from __future__ import annotations

import re

__all__ = ("strip_unity_rich_text",)

_UNITY_RT_SIZE = re.compile(r"<size=(?:\d+)>(.+?)</size>")
_UNITY_RT_COLOR = re.compile(r"<color=(?:[#]?[\w\d]+)>(.+?)</color>")
_UNITY_RT_MAT = re.compile(r"<material=(?:[\d+])>(.+?)</material>")


def strip_unity_rich_text(text: str, *, only_tags: list[str] | None = None) -> str:
    basic_format = only_tags or ["b", "i", "unbreak", "s", "u", "lowercase", "uppercase", "smallcaps", "nobr", "sup"]
    for tag in basic_format:
        text = text.replace(f"<{tag}>", "").replace(f"</{tag}>", "")

    complex_formats = [_UNITY_RT_SIZE, _UNITY_RT_COLOR, _UNITY_RT_MAT]
    for tag in complex_formats:
        text = tag.sub(r"\1", text)
    return text.replace("\\n", "\n")
