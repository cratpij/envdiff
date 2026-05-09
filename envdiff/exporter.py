"""Export diff results to various output formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.diff import EnvDiffResult

OutputFormat = Literal["json", "csv", "markdown"]


def export_json(result: EnvDiffResult, indent: int = 2) -> str:
    """Serialize an EnvDiffResult to a JSON string."""
    data = {
        "missing_in_right": sorted(result.missing_in_right),
        "missing_in_left": sorted(result.missing_in_left),
        "mismatched": {
            k: {"left": lv, "right": rv}
            for k, (lv, rv) in sorted(result.mismatched.items())
        },
    }
    return json.dumps(data, indent=indent)


def export_csv(result: EnvDiffResult) -> str:
    """Serialize an EnvDiffResult to a CSV string.

    Columns: key, status, left_value, right_value
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "left_value", "right_value"])

    for key in sorted(result.missing_in_right):
        writer.writerow([key, "missing_in_right", "", ""])

    for key in sorted(result.missing_in_left):
        writer.writerow([key, "missing_in_left", "", ""])

    for key, (lv, rv) in sorted(result.mismatched.items()):
        writer.writerow([key, "mismatched", lv, rv])

    return buf.getvalue()


def export_markdown(result: EnvDiffResult) -> str:
    """Serialize an EnvDiffResult to a Markdown table string."""
    lines: list[str] = []
    lines.append("| Key | Status | Left Value | Right Value |")
    lines.append("|-----|--------|------------|-------------|")

    for key in sorted(result.missing_in_right):
        lines.append(f"| `{key}` | missing in right | | |")

    for key in sorted(result.missing_in_left):
        lines.append(f"| `{key}` | missing in left | | |")

    for key, (lv, rv) in sorted(result.mismatched.items()):
        lines.append(f"| `{key}` | mismatched | `{lv}` | `{rv}` |")

    if not (result.missing_in_right or result.missing_in_left or result.mismatched):
        lines.append("| _(no differences)_ | | | |")

    return "\n".join(lines) + "\n"


def export(result: EnvDiffResult, fmt: OutputFormat) -> str:
    """Dispatch export to the appropriate formatter.

    Args:
        result: The diff result to export.
        fmt: The desired output format. Must be one of ``"json"``,
            ``"csv"``, or ``"markdown"``.

    Returns:
        A string representation of the diff in the requested format.

    Raises:
        ValueError: If *fmt* is not a recognised output format.
    """
    if fmt == "json":
        return export_json(result)
    if fmt == "csv":
        return export_csv(result)
    if fmt == "markdown":
        return export_markdown(result)
    raise ValueError(
        f"Unsupported export format: {fmt!r}. "
        f"Valid formats are: {', '.join(OutputFormat.__args__)}"
    )
