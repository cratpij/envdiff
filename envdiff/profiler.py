"""Profile .env files: count keys, detect duplicates, measure value lengths."""

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class EnvProfile:
    """Statistical profile of a single .env file."""

    path: str
    total_keys: int = 0
    empty_values: List[str] = field(default_factory=list)
    long_values: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)
    avg_value_length: float = 0.0
    max_value_length: int = 0
    max_value_key: str = ""

    def has_issues(self) -> bool:
        return bool(self.empty_values or self.duplicate_keys)

    def summary(self) -> str:
        lines = [f"Profile: {self.path}", f"  Total keys : {self.total_keys}"]
        if self.empty_values:
            lines.append(f"  Empty values: {', '.join(self.empty_values)}")
        if self.duplicate_keys:
            lines.append(f"  Duplicate keys: {', '.join(self.duplicate_keys)}")
        lines.append(f"  Avg value length: {self.avg_value_length:.1f}")
        lines.append(f"  Max value length: {self.max_value_length} ({self.max_value_key})")
        if self.long_values:
            lines.append(f"  Long values (>64): {', '.join(self.long_values)}")
        return "\n".join(lines)


LONG_VALUE_THRESHOLD = 64


def profile_env(env: Dict[str, str], path: str = "<dict>") -> EnvProfile:
    """Build an EnvProfile from a parsed env dict."""
    profile = EnvProfile(path=path, total_keys=len(env))

    if not env:
        return profile

    lengths = [len(v) for v in env.values()]
    profile.avg_value_length = sum(lengths) / len(lengths)
    profile.max_value_length = max(lengths)

    for key, value in env.items():
        if len(value) == profile.max_value_length:
            profile.max_value_key = key
        if value == "":
            profile.empty_values.append(key)
        if len(value) > LONG_VALUE_THRESHOLD:
            profile.long_values.append(key)

    return profile


def profile_env_file(path: str) -> EnvProfile:
    """Parse a .env file and return its profile."""
    env = parse_env_file(path)
    return profile_env(env, path=path)


def profile_raw_lines(path: str) -> List[str]:
    """Return duplicate keys found by scanning raw lines (before dedup by dict)."""
    seen: Dict[str, int] = {}
    duplicates: List[str] = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key = line.split("=", 1)[0].strip()
                    seen[key] = seen.get(key, 0) + 1
    except FileNotFoundError:
        raise
    for key, count in seen.items():
        if count > 1:
            duplicates.append(key)
    return duplicates
