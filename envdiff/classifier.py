"""Classify env keys into categories based on naming patterns and value types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Category name -> list of glob-style prefix/substring patterns
_DEFAULT_RULES: Dict[str, List[str]] = {
    "database": ["DB_", "DATABASE_", "POSTGRES_", "MYSQL_", "MONGO_", "REDIS_"],
    "auth": ["AUTH_", "JWT_", "OAUTH_", "SECRET", "TOKEN", "PASSWORD", "PASSWD"],
    "network": ["HOST", "PORT", "URL", "URI", "ENDPOINT", "DOMAIN", "ADDR"],
    "feature_flag": ["FEATURE_", "FLAG_", "ENABLE_", "DISABLE_", "FF_"],
    "logging": ["LOG_", "LOGGING_", "DEBUG", "VERBOSE"],
    "cloud": ["AWS_", "GCP_", "AZURE_", "S3_", "GCS_"],
}


@dataclass
class ClassificationResult:
    source: str
    categories: Dict[str, List[str]] = field(default_factory=dict)  # category -> keys
    uncategorized: List[str] = field(default_factory=list)

    def keys_in(self, category: str) -> List[str]:
        return self.categories.get(category, [])

    def category_of(self, key: str) -> Optional[str]:
        for cat, keys in self.categories.items():
            if key in keys:
                return cat
        return None

    def summary(self) -> str:
        lines = [f"Classification: {self.source}"]
        for cat, keys in sorted(self.categories.items()):
            lines.append(f"  {cat}: {len(keys)} key(s)")
        lines.append(f"  uncategorized: {len(self.uncategorized)} key(s)")
        return "\n".join(lines)


def _match_category(key: str, rules: Dict[str, List[str]]) -> Optional[str]:
    upper = key.upper()
    for category, patterns in rules.items():
        for pattern in patterns:
            if pattern.upper() in upper:
                return category
    return None


def classify_env(
    env: Dict[str, str],
    source: str = "<env>",
    rules: Optional[Dict[str, List[str]]] = None,
) -> ClassificationResult:
    effective_rules = rules if rules is not None else _DEFAULT_RULES
    categories: Dict[str, List[str]] = {}
    uncategorized: List[str] = []

    for key in env:
        cat = _match_category(key, effective_rules)
        if cat:
            categories.setdefault(cat, []).append(key)
        else:
            uncategorized.append(key)

    return ClassificationResult(
        source=source,
        categories=categories,
        uncategorized=uncategorized,
    )


def classify_env_file(
    path: str,
    rules: Optional[Dict[str, List[str]]] = None,
) -> ClassificationResult:
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return classify_env(env, source=path, rules=rules)
