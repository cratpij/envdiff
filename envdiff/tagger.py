"""Tag env keys with metadata labels (e.g. required, optional, secret, deprecated)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set

KNOWN_TAGS: FrozenSet[str] = frozenset({"required", "optional", "secret", "deprecated", "internal"})


@dataclass
class TagResult:
    source: str
    tags: Dict[str, Set[str]] = field(default_factory=dict)  # key -> set of tags
    unknown_tags: List[str] = field(default_factory=list)

    def keys_with_tag(self, tag: str) -> List[str]:
        """Return all keys that have the given tag."""
        return [k for k, t in self.tags.items() if tag in t]

    def tags_for(self, key: str) -> Set[str]:
        """Return tags for a specific key, or empty set."""
        return self.tags.get(key, set())

    def has_tag(self, key: str, tag: str) -> bool:
        return tag in self.tags.get(key, set())

    def summary(self) -> str:
        total = len(self.tags)
        if total == 0:
            return "No keys tagged."
        parts = []
        for tag in sorted(KNOWN_TAGS):
            count = len(self.keys_with_tag(tag))
            if count:
                parts.append(f"{tag}={count}")
        tag_summary = ", ".join(parts) if parts else "none"
        return f"{total} key(s) tagged: {tag_summary}"


def tag_env(
    env: Dict[str, str],
    tag_map: Dict[str, List[str]],
    source: str = "<dict>",
) -> TagResult:
    """Apply tags from tag_map to keys present in env.

    tag_map: {key: [tag, ...]} — keys not in env are silently skipped.
    Tags not in KNOWN_TAGS are recorded in unknown_tags.
    """
    result = TagResult(source=source)
    unknown: Set[str] = set()

    for key, tag_list in tag_map.items():
        if key not in env:
            continue
        valid_tags: Set[str] = set()
        for t in tag_list:
            if t not in KNOWN_TAGS:
                unknown.add(t)
            else:
                valid_tags.add(t)
        if valid_tags:
            result.tags[key] = valid_tags

    result.unknown_tags = sorted(unknown)
    return result


def tag_env_file(
    path: str,
    tag_map: Dict[str, List[str]],
) -> TagResult:
    """Parse an env file and apply tags."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return tag_env(env, tag_map, source=path)
