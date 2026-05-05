"""Patch a .env file by applying missing keys from another environment."""

from __future__ import annotations

from typing import Dict, List, Optional

from envdiff.diff import EnvDiffResult, diff_envs
from envdiff.parser import parse_env_file


def patch_env(
    base: Dict[str, str],
    donor: Dict[str, str],
    result: EnvDiffResult,
    placeholder: str = "",
    overwrite_mismatched: bool = False,
) -> Dict[str, str]:
    """Return a new dict with keys from *donor* patched into *base*.

    Only keys that are *missing in base* (i.e. ``result.missing_in_left``)
    are added.  If *overwrite_mismatched* is ``True``, mismatched values
    are also overwritten with the donor's value.

    Args:
        base: The environment to patch.
        donor: The environment supplying missing/replacement values.
        result: Pre-computed diff result (``diff_envs(base, donor)``).
        placeholder: Value to use when the donor key has no value.
        overwrite_mismatched: Replace mismatched values with donor values.

    Returns:
        A new dict representing the patched environment.
    """
    patched = dict(base)

    for key in result.missing_in_left:
        patched[key] = donor.get(key, placeholder)

    if overwrite_mismatched:
        for key in result.mismatched:
            patched[key] = donor.get(key, placeholder)

    return patched


def patch_env_to_string(
    patched: Dict[str, str],
    added_keys: List[str],
    overwritten_keys: Optional[List[str]] = None,
) -> str:
    """Serialise *patched* env dict to .env file content.

    Added/overwritten keys receive a trailing ``# PATCHED`` comment.
    """
    overwritten_keys = overwritten_keys or []
    flagged = set(added_keys) | set(overwritten_keys)
    lines: list[str] = []
    for key in sorted(patched):
        value = patched[key]
        suffix = "  # PATCHED" if key in flagged else ""
        lines.append(f"{key}={value}{suffix}")
    return "\n".join(lines)


def patch_env_files(
    base_path: str,
    donor_path: str,
    overwrite_mismatched: bool = False,
    placeholder: str = "",
) -> str:
    """Parse two .env files and return patched .env content as a string."""
    base = parse_env_file(base_path)
    donor = parse_env_file(donor_path)
    result = diff_envs(base, donor)
    patched = patch_env(
        base, donor, result,
        placeholder=placeholder,
        overwrite_mismatched=overwrite_mismatched,
    )
    overwritten = list(result.mismatched) if overwrite_mismatched else []
    return patch_env_to_string(patched, list(result.missing_in_left), overwritten)
