"""Format and print SampleResult objects."""

from __future__ import annotations

from envdiff.sampler import SampleResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_sample_report(
    result: SampleResult,
    *,
    color: bool = True,
    filename: str | None = None,
) -> str:
    label = filename or result.source
    lines: list[str] = []

    header = f"Sample Report: {label}"
    lines.append(_colorize(header, "1;34") if color else header)
    lines.append(_colorize(result.summary(), "36") if color else result.summary())
    lines.append("")

    if not result.sampled:
        msg = "  (no keys sampled)"
        lines.append(_colorize(msg, "33") if color else msg)
    else:
        for key, value in sorted(result.sampled.items()):
            key_part = _colorize(key, "32") if color else key
            lines.append(f"  {key_part} = {value}")

    return "\n".join(lines)


def print_sample_report(
    result: SampleResult,
    *,
    color: bool = True,
    filename: str | None = None,
) -> None:
    print(format_sample_report(result, color=color, filename=filename))
