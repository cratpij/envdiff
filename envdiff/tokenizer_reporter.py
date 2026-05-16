"""Format and print tokenizer reports."""
from __future__ import annotations

from envdiff.tokenizer import TokenizeResult, TokenType

_COLORS = {
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
}


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def format_tokenize_report(
    result: TokenizeResult,
    filename: str | None = None,
    use_color: bool = True,
) -> str:
    label = filename or result.source or "<input>"
    lines = [
        _colorize(f"Tokenize Report: {label}", "cyan", use_color),
        _colorize(result.summary(), "green" if not result.malformed else "yellow", use_color),
        "",
    ]

    if result.assignments:
        lines.append(_colorize("Assignments:", "cyan", use_color))
        for t in result.assignments:
            lines.append(f"  L{t.line_number:>3}  {t.key} = {t.value}")
        lines.append("")

    if result.comments:
        lines.append(_colorize("Comments:", "cyan", use_color))
        for t in result.comments:
            lines.append(f"  L{t.line_number:>3}  {t.raw.strip()}")
        lines.append("")

    if result.malformed:
        lines.append(_colorize("Malformed lines:", "red", use_color))
        for t in result.malformed:
            lines.append(
                _colorize(f"  L{t.line_number:>3}  {t.raw.strip()}", "red", use_color)
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def print_tokenize_report(
    result: TokenizeResult,
    filename: str | None = None,
    use_color: bool = True,
) -> None:
    print(format_tokenize_report(result, filename=filename, use_color=use_color), end="")
