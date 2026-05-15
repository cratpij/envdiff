"""Format and print reports for PruneResult."""
from __future__ import annotations

import sys
from typing import Optional

from envdiff.pruner import PruneResult

_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _colorize(text: str, color: str, *, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{_RESET}"


def format_prune_report(
    result: PruneResult,
    *,
    filename: Optional[str] = None,
    use_color: bool = True,
) -> str:
    label = filename or result.source
    lines: list[str] = []
    lines.append(
        _colorize(f"=== Prune Report: {label} ===", _BOLD, use_color=use_color)
    )
    lines.append(f"Reference : {result.reference}")
    lines.append(
        f"Keys kept : {_colorize(str(len(result.kept_keys)), _GREEN, use_color=use_color)}"
    )
    lines.append(
        f"Keys removed: "
        + _colorize(str(result.total_removed), _RED if result.total_removed else _GREEN, use_color=use_color)
    )

    if result.removed_keys:
        lines.append("")
        lines.append(_colorize("Removed keys:", _YELLOW, use_color=use_color))
        for key in result.removed_keys:
            lines.append(f"  - {_colorize(key, _RED, use_color=use_color)}")
    else:
        lines.append(
            _colorize("  All keys present in reference — nothing pruned.", _GREEN, use_color=use_color)
        )

    if result.kept_keys:
        lines.append("")
        lines.append("Kept keys:")
        for key in result.kept_keys:
            lines.append(f"  + {_colorize(key, _GREEN, use_color=use_color)}")

    return "\n".join(lines)


def print_prune_report(
    result: PruneResult,
    *,
    filename: Optional[str] = None,
    use_color: bool = True,
    file=None,
) -> None:
    if file is None:
        file = sys.stdout
    print(format_prune_report(result, filename=filename, use_color=use_color), file=file)
