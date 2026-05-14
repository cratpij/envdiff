"""Format and print DigestResult reports."""

from __future__ import annotations

import sys
from typing import Optional

from envdiff.digester import DigestResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_RED = "\033[31m"


def _colorize(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_digest_report(
    result: DigestResult,
    filename: Optional[str] = None,
    use_color: bool = True,
) -> str:
    label = filename or result.source
    lines = [
        _colorize(f"=== Digest Report: {label} ===", _BOLD, use_color),
        f"Total keys : {result.total_keys}",
    ]

    breakdown = result.type_breakdown

    def _row(kind: str, keys: list, color: str) -> None:
        if keys:
            label_str = _colorize(f"  {kind} ({len(keys)})", color, use_color)
            lines.append(label_str + ": " + ", ".join(keys))

    _row("empty", result.empty_keys, _RED)
    _row("boolean", result.boolean_keys, _CYAN)
    _row("numeric", result.numeric_keys, _CYAN)
    _row("url", result.url_keys, _CYAN)
    _row(
        f"long (>={result.long_value_threshold} chars)",
        result.long_value_keys,
        _YELLOW,
    )

    if not any(breakdown.values()):
        lines.append(_colorize("  all values look standard", _GREEN, use_color))

    return "\n".join(lines)


def print_digest_report(
    result: DigestResult,
    filename: Optional[str] = None,
    use_color: bool = True,
    file=None,
) -> None:
    if file is None:
        file = sys.stdout
    print(format_digest_report(result, filename=filename, use_color=use_color), file=file)
