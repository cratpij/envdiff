"""Format and print reports for TagResult."""
from __future__ import annotations

import sys
from typing import IO

from envdiff.tagger import TagResult, KNOWN_TAGS

_COLORS = {
    "required": "\033[91m",    # red
    "secret": "\033[95m",      # magenta
    "deprecated": "\033[93m",  # yellow
    "optional": "\033[94m",    # blue
    "internal": "\033[90m",    # grey
    "reset": "\033[0m",
}


def _colorize(tag: str, text: str, use_color: bool) -> str:
    if not use_color:
        return text
    color = _COLORS.get(tag, "")
    return f"{color}{text}{_COLORS['reset']}"


def format_tag_report(result: TagResult, use_color: bool = True) -> str:
    lines: list[str] = []
    lines.append(f"Tag report: {result.source}")
    lines.append("-" * 40)

    if not result.tags:
        lines.append("  No tagged keys found.")
    else:
        for tag in sorted(KNOWN_TAGS):
            keys = result.keys_with_tag(tag)
            if not keys:
                continue
            header = _colorize(tag, f"[{tag.upper()}]", use_color)
            lines.append(f"  {header}")
            for key in sorted(keys):
                lines.append(f"    - {key}")

    if result.unknown_tags:
        lines.append("")
        lines.append(f"  Unknown tags (ignored): {', '.join(result.unknown_tags)}")

    lines.append("")
    lines.append(f"  {result.summary()}")
    return "\n".join(lines)


def print_tag_report(
    result: TagResult,
    use_color: bool = True,
    file: IO[str] = sys.stdout,
) -> None:
    print(format_tag_report(result, use_color=use_color), file=file)
