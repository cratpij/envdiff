"""Digest an env dict into a structured summary of key statistics and patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DigestResult:
    source: str
    total_keys: int
    empty_keys: List[str] = field(default_factory=list)
    numeric_keys: List[str] = field(default_factory=list)
    boolean_keys: List[str] = field(default_factory=list)
    url_keys: List[str] = field(default_factory=list)
    long_value_keys: List[str] = field(default_factory=list)
    long_value_threshold: int = 100

    @property
    def has_empty(self) -> bool:
        return bool(self.empty_keys)

    @property
    def type_breakdown(self) -> Dict[str, int]:
        return {
            "empty": len(self.empty_keys),
            "numeric": len(self.numeric_keys),
            "boolean": len(self.boolean_keys),
            "url": len(self.url_keys),
            "long": len(self.long_value_keys),
        }

    def summary(self) -> str:
        lines = [f"Digest: {self.source} — {self.total_keys} keys"]
        for kind, count in self.type_breakdown.items():
            if count:
                lines.append(f"  {kind}: {count}")
        if not any(self.type_breakdown.values()):
            lines.append("  all values look standard")
        return "\n".join(lines)


_BOOLEAN_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _is_boolean(value: str) -> bool:
    return value.lower() in _BOOLEAN_VALUES


def _is_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "ftp://", "postgres://", "mysql://", "redis://"))


def digest_env(
    env: Dict[str, str],
    source: str = "<env>",
    long_value_threshold: int = 100,
) -> DigestResult:
    """Analyse an env dict and return a DigestResult with categorised keys."""
    empty: List[str] = []
    numeric: List[str] = []
    boolean: List[str] = []
    url: List[str] = []
    long: List[str] = []

    for key, value in env.items():
        if value == "":
            empty.append(key)
            continue
        if _is_url(value):
            url.append(key)
        elif _is_boolean(value):
            boolean.append(key)
        elif _is_numeric(value):
            numeric.append(key)
        if len(value) >= long_value_threshold:
            long.append(key)

    return DigestResult(
        source=source,
        total_keys=len(env),
        empty_keys=sorted(empty),
        numeric_keys=sorted(numeric),
        boolean_keys=sorted(boolean),
        url_keys=sorted(url),
        long_value_keys=sorted(long),
        long_value_threshold=long_value_threshold,
    )


def digest_env_file(path: str, long_value_threshold: int = 100) -> DigestResult:
    """Parse an env file and return its DigestResult."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return digest_env(env, source=path, long_value_threshold=long_value_threshold)
