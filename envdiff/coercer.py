"""Type coercion for .env values — convert string values to inferred Python types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


_TRUE_STRINGS = {"true", "yes", "1", "on"}
_FALSE_STRINGS = {"false", "no", "0", "off"}


def _coerce_value(value: str) -> Any:
    """Attempt to coerce a single string value to bool, int, float, or leave as str."""
    stripped = value.strip()
    if stripped.lower() in _TRUE_STRINGS:
        return True
    if stripped.lower() in _FALSE_STRINGS:
        return False
    try:
        return int(stripped)
    except ValueError:
        pass
    try:
        return float(stripped)
    except ValueError:
        pass
    return stripped


@dataclass
class CoercionResult:
    source: str
    coerced: Dict[str, Any] = field(default_factory=dict)
    original: Dict[str, str] = field(default_factory=dict)

    def changed_keys(self) -> List[str]:
        """Keys whose type changed after coercion."""
        return [
            k for k, v in self.coerced.items()
            if not isinstance(v, str)
        ]

    def summary(self) -> str:
        changed = self.changed_keys()
        if not changed:
            return f"{self.source}: all values remain strings (no coercion applied)"
        return (
            f"{self.source}: {len(changed)} key(s) coerced "
            f"({', '.join(sorted(changed))})"
        )


def coerce_env(env: Dict[str, str], source: str = "<env>") -> CoercionResult:
    """Coerce all values in an env dict to their inferred Python types."""
    coerced = {k: _coerce_value(v) for k, v in env.items()}
    return CoercionResult(source=source, coerced=coerced, original=dict(env))


def coerce_env_file(path: str) -> CoercionResult:
    """Parse a .env file and coerce its values."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return coerce_env(env, source=path)
