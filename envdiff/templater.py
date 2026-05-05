"""Generate .env.example templates from parsed env files or diff results."""

from __future__ import annotations

from typing import Dict, Iterable, Optional

from envdiff.diff import EnvDiffResult


def _placeholder(key: str, value: Optional[str] = None) -> str:
    """Return a placeholder string for a key, optionally hinting at its type."""
    if value is not None:
        # Preserve non-sensitive looking values as hints
        if value.lower() in ("true", "false", "1", "0"):
            return value
        if value.isdigit():
            return value
    return f"<{key.lower()}>"


def generate_template(
    env: Dict[str, str],
    *,
    include_values: bool = False,
    comment_header: Optional[str] = None,
) -> str:
    """Generate a .env.example template from a parsed env dictionary.

    Args:
        env: Mapping of key -> value from a parsed .env file.
        include_values: If True, keep original values; otherwise use placeholders.
        comment_header: Optional comment block prepended to the output.

    Returns:
        A string suitable for writing as a .env.example file.
    """
    lines: list[str] = []

    if comment_header:
        for line in comment_header.splitlines():
            lines.append(f"# {line}" if not line.startswith("#") else line)
        lines.append("")

    for key in sorted(env.keys()):
        value = env[key] if include_values else _placeholder(key, env[key])
        lines.append(f"{key}={value}")

    return "\n".join(lines) + ("\n" if lines else "")


def generate_template_from_diff(
    result: EnvDiffResult,
    *,
    include_values: bool = False,
    comment_header: Optional[str] = None,
) -> str:
    """Generate a unified .env.example template from a diff result.

    Combines keys from both sides of the diff.  Mismatched keys use the
    left-hand value as the canonical hint.

    Args:
        result: An EnvDiffResult produced by diff_envs.
        include_values: If True, keep original values; otherwise use placeholders.
        comment_header: Optional comment block prepended to the output.

    Returns:
        A string suitable for writing as a .env.example file.
    """
    merged: Dict[str, str] = {}
    merged.update(result.left_only)
    merged.update(result.right_only)
    for key, (left_val, _right_val) in result.mismatched.items():
        merged[key] = left_val

    return generate_template(merged, include_values=include_values, comment_header=comment_header)
