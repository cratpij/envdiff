"""Sort and group environment variable keys for structured comparison."""

from typing import Dict, List, Tuple


def sort_keys_alphabetically(env: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items()))


def group_keys_by_prefix(
    env: Dict[str, str], separator: str = "_"
) -> Dict[str, Dict[str, str]]:
    """Group environment variables by their prefix (first segment before separator).

    Keys without the separator are grouped under the empty-string prefix.

    Args:
        env: Mapping of env var names to values.
        separator: Character used to split the key into prefix and remainder.

    Returns:
        A dict mapping each prefix to a sub-dict of matching key/value pairs.
    """
    groups: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        if separator in key:
            prefix, _ = key.split(separator, 1)
        else:
            prefix = ""
        groups.setdefault(prefix, {})[key] = value
    return groups


def sorted_diff_keys(
    left: Dict[str, str], right: Dict[str, str]
) -> Tuple[List[str], List[str], List[str]]:
    """Return sorted lists of keys: only_in_left, only_in_right, in_both.

    Args:
        left: First environment mapping.
        right: Second environment mapping.

    Returns:
        A tuple of three sorted lists:
          - keys present only in *left*
          - keys present only in *right*
          - keys present in both
    """
    left_keys = set(left)
    right_keys = set(right)

    only_left = sorted(left_keys - right_keys)
    only_right = sorted(right_keys - left_keys)
    in_both = sorted(left_keys & right_keys)

    return only_left, only_right, in_both
