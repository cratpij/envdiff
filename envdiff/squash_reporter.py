"""squash_reporter.py — Format and print squash results."""
from __future__ import annotations

from envdiff.squasher import SquashResult

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_squash_report(
    result: SquashResult,
    filename: str = "",
    use_color: bool = True,
) -> str:
    lines: list[str] = []
    header = f"Squash Report{': ' + filename if filename else ''}"
    lines.append(_colorize(f"=== {header} ===", _BOLD, use_color))
    lines.append(f"Sources : {', '.join(result.sources)}")
    lines.append(result.summary())
    lines.append("")

    if not result.has_conflicts():
        lines.append(_colorize("No conflicts — all sources agree.", _GREEN, use_color))
    else:
        lines.append(
            _colorize(
                f"{result.conflict_count()} conflict(s):", _RED, use_color
            )
        )
        for key, src_list in sorted(result.conflicts.items()):
            sources_str = ", ".join(src_list)
            winner = result.origins[key]
            value = result.squashed[key]
            line = (
                f"  {_colorize(key, _YELLOW, use_color)}"
                f" — conflict in [{sources_str}]"
                f" — kept from {_colorize(winner, _CYAN, use_color)}"
                f" = {value!r}"
            )
            lines.append(line)

    lines.append("")
    lines.append(f"{len(result.squashed)} total key(s) in squashed output.")
    return "\n".join(lines)


def print_squash_report(
    result: SquashResult,
    filename: str = "",
    use_color: bool = True,
) -> None:
    print(format_squash_report(result, filename=filename, use_color=use_color))
