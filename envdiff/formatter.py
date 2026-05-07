"""Format env dicts into various string representations."""
from __future__ import annotations

from typing import Dict, Optional


def format_env_as_dotenv(env: Dict[str, str], header: Optional[str] = None) -> str:
    """Render an env dict as a .env file string.

    Args:
        env: Mapping of key -> value.
        header: Optional comment header placed at the top of the output.

    Returns:
        A string suitable for writing to a .env file.
    """
    lines: list[str] = []
    if header:
        for line in header.splitlines():
            lines.append(f"# {line}" if not line.startswith("#") else line)
        lines.append("")

    for key in sorted(env):
        value = env[key]
        # Quote values that contain spaces or are empty
        if not value:
            lines.append(f'{key}=""')
        elif " " in value or "\t" in value:
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")

    return "\n".join(lines) + ("\n" if lines else "")


def format_env_as_export(env: Dict[str, str], header: Optional[str] = None) -> str:
    """Render an env dict as shell export statements.

    Args:
        env: Mapping of key -> value.
        header: Optional comment header.

    Returns:
        A string of ``export KEY=VALUE`` lines.
    """
    lines: list[str] = []
    if header:
        for line in header.splitlines():
            lines.append(f"# {line}" if not line.startswith("#") else line)
        lines.append("")

    for key in sorted(env):
        value = env[key]
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')

    return "\n".join(lines) + ("\n" if lines else "")


def format_env_as_ini(env: Dict[str, str], section: str = "env") -> str:
    """Render an env dict as an INI-style section.

    Args:
        env: Mapping of key -> value.
        section: Section header name.

    Returns:
        An INI-formatted string.
    """
    lines: list[str] = [f"[{section}]"]
    for key in sorted(env):
        lines.append(f"{key} = {env[key]}")
    return "\n".join(lines) + "\n"
