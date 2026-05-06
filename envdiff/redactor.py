"""Redact sensitive values in env dicts before display or export."""

from __future__ import annotations

import re
from typing import Dict, FrozenSet, Optional

# Keys whose values should be fully redacted
_SENSITIVE_PATTERNS: list[re.Pattern] = [
    re.compile(r"(SECRET|PASSWORD|PASSWD|TOKEN|API_KEY|PRIVATE|AUTH|CREDENTIAL)", re.IGNORECASE),
]

REDACTED_PLACEHOLDER = "***REDACTED***"


def is_sensitive(key: str) -> bool:
    """Return True if the key name looks like it holds a sensitive value."""
    return any(pat.search(key) for pat in _SENSITIVE_PATTERNS)


def redact_value(key: str, value: str, extra_keys: Optional[FrozenSet[str]] = None) -> str:
    """Return the redacted placeholder if the key is sensitive, else the original value."""
    sensitive_keys: FrozenSet[str] = extra_keys or frozenset()
    if is_sensitive(key) or key in sensitive_keys:
        return REDACTED_PLACEHOLDER
    return value


def redact_env(
    env: Dict[str, str],
    extra_keys: Optional[FrozenSet[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by the redacted placeholder.

    Args:
        env: Mapping of environment variable names to their values.
        extra_keys: Additional key names (beyond the built-in patterns) to redact.

    Returns:
        A new dict with the same keys but sensitive values replaced.
    """
    return {k: redact_value(k, v, extra_keys) for k, v in env.items()}


def redact_env_file(
    path: str,
    extra_keys: Optional[FrozenSet[str]] = None,
) -> Dict[str, str]:
    """Parse *path* and return a redacted copy of its contents."""
    from envdiff.parser import parse_env_file  # local import to avoid circular deps

    env = parse_env_file(path)
    return redact_env(env, extra_keys)
