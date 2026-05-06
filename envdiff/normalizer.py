"""Normalize .env file keys and values for consistent comparison."""

from __future__ import annotations

from typing import Dict, Optional


def normalize_key(key: str) -> str:
    """Normalize a key to uppercase with no surrounding whitespace."""
    return key.strip().upper()


def normalize_value(value: str) -> str:
    """Normalize a value by stripping surrounding whitespace."""
    return value.strip()


def normalize_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with all keys uppercased and values stripped.

    If two keys collide after normalization the last one wins.
    """
    return {normalize_key(k): normalize_value(v) for k, v in env.items()}


def normalize_env_file(
    path: str,
    encoding: str = "utf-8",
) -> Dict[str, str]:
    """Parse *path* and return a normalized env dict.

    Delegates parsing to :func:`envdiff.parser.parse_env_file` so that
    comment / blank-line stripping and quote removal are handled there.
    """
    from envdiff.parser import parse_env_file  # local import to avoid cycles

    raw = parse_env_file(path, encoding=encoding)
    return normalize_env(raw)


def diff_normalized(
    left: Dict[str, str],
    right: Dict[str, str],
    *,
    left_name: str = "left",
    right_name: str = "right",
) -> Dict[str, object]:
    """Compare two already-normalized env dicts and return a summary dict.

    Returns a mapping with keys:
      - ``missing_in_right``  – keys present in *left* but not *right*
      - ``missing_in_left``   – keys present in *right* but not *left*
      - ``mismatched``        – keys present in both but with different values
    """
    left_keys = set(left)
    right_keys = set(right)

    missing_in_right = sorted(left_keys - right_keys)
    missing_in_left = sorted(right_keys - left_keys)
    mismatched = {
        k: {left_name: left[k], right_name: right[k]}
        for k in sorted(left_keys & right_keys)
        if left[k] != right[k]
    }

    return {
        "missing_in_right": missing_in_right,
        "missing_in_left": missing_in_left,
        "mismatched": mismatched,
    }
