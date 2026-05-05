"""Parser module for reading and parsing .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_PATTERN = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)
COMMENT_PATTERN = re.compile(r'^\s*#')


def parse_env_file(filepath: str | Path) -> Dict[str, str]:
    """Parse a .env file and return a dictionary of key-value pairs.

    Args:
        filepath: Path to the .env file.

    Returns:
        A dictionary mapping environment variable names to their values.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file contains a malformed line.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    env_vars: Dict[str, str] = {}

    with path.open("r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")

            # Skip empty lines and comments
            if not line.strip() or COMMENT_PATTERN.match(line):
                continue

            match = ENV_LINE_PATTERN.match(line)
            if not match:
                raise ValueError(
                    f"Malformed line {line_num} in '{filepath}': {line!r}"
                )

            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            env_vars[key] = value

    return env_vars


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
    return value
