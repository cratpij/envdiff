"""Write export output to a file or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from envdiff.diff import EnvDiffResult
from envdiff.exporter import OutputFormat, export


def write_export(
    result: EnvDiffResult,
    fmt: OutputFormat,
    output_path: Optional[str] = None,
) -> None:
    """Export *result* in *fmt* format and write to *output_path* or stdout.

    Parameters
    ----------
    result:
        The diff result to export.
    fmt:
        One of ``"json"``, ``"csv"``, or ``"markdown"``.
    output_path:
        Filesystem path to write to.  When ``None`` the output is written to
        *stdout*.
    """
    content = export(result, fmt)

    if output_path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
