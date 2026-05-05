"""Annotate .env files with comments describing diff status per key."""

from __future__ import annotations

from typing import Dict, Optional

from envdiff.diff import EnvDiffResult, diff_envs
from envdiff.parser import parse_env_file

_STATUS_LABELS: Dict[str, str] = {
    "missing_in_right": "MISSING IN RIGHT",
    "missing_in_left": "MISSING IN LEFT",
    "mismatch": "VALUE MISMATCH",
    "ok": "OK",
}


def annotate_env(
    env: Dict[str, str],
    result: EnvDiffResult,
    side: str = "left",
) -> str:
    """Return an annotated .env string for *env* based on *result*.

    Args:
        env: The parsed environment dict to annotate.
        result: A diff result produced by ``diff_envs``.
        side: Either ``"left"`` or ``"right"`` — controls which side's
              missing-key label is used.

    Returns:
        Multi-line string with one ``KEY=VALUE  # STATUS`` line per key.
    """
    if side not in ("left", "right"):
        raise ValueError(f"side must be 'left' or 'right', got {side!r}")

    lines: list[str] = []
    all_keys = sorted(
        set(env)
        | set(result.missing_in_right)
        | set(result.missing_in_left)
        | set(result.mismatched)
    )

    for key in all_keys:
        if key in result.mismatched:
            status = _STATUS_LABELS["mismatch"]
        elif key in result.missing_in_right and side == "left":
            status = _STATUS_LABELS["missing_in_right"]
        elif key in result.missing_in_left and side == "right":
            status = _STATUS_LABELS["missing_in_left"]
        elif key in result.missing_in_left and side == "left":
            # Key absent from left — show placeholder
            lines.append(f"# {key}=  # {_STATUS_LABELS['missing_in_left']}")
            continue
        elif key in result.missing_in_right and side == "right":
            lines.append(f"# {key}=  # {_STATUS_LABELS['missing_in_right']}")
            continue
        else:
            status = _STATUS_LABELS["ok"]

        value = env.get(key, "")
        lines.append(f"{key}={value}  # {status}")

    return "\n".join(lines)


def annotate_env_files(
    left_path: str,
    right_path: str,
    side: str = "left",
) -> str:
    """Parse two .env files, diff them, and return an annotated string."""
    left = parse_env_file(left_path)
    right = parse_env_file(right_path)
    result = diff_envs(left, right)
    env = left if side == "left" else right
    return annotate_env(env, result, side=side)
