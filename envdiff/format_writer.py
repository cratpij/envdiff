"""Write formatted env output to stdout or a file."""
from __future__ import annotations

import sys
from typing import Dict, Optional

from envdiff.formatter import format_env_as_dotenv, format_env_as_export, format_env_as_ini

_FORMATS = {
    "dotenv": format_env_as_dotenv,
    "export": format_env_as_export,
    "ini": format_env_as_ini,
}

SUPPORTED_FORMATS = list(_FORMATS.keys())


def write_formatted(
    env: Dict[str, str],
    fmt: str = "dotenv",
    output_path: Optional[str] = None,
    header: Optional[str] = None,
    section: str = "env",
) -> None:
    """Render *env* in the requested format and write to *output_path* or stdout.

    Args:
        env: Key/value pairs to format.
        fmt: One of ``'dotenv'``, ``'export'``, or ``'ini'``.
        output_path: File path to write to.  ``None`` means stdout.
        header: Optional comment header (ignored for ``'ini'`` format).
        section: INI section name (only used when *fmt* is ``'ini'``).

    Raises:
        ValueError: If *fmt* is not a supported format string.
    """
    if fmt not in _FORMATS:
        raise ValueError(
            f"Unsupported format {fmt!r}. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    if fmt == "ini":
        content = format_env_as_ini(env, section=section)
    else:
        content = _FORMATS[fmt](env, header=header)  # type: ignore[call-arg]

    if output_path is None:
        sys.stdout.write(content)
    else:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(content)
