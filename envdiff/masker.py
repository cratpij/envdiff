"""masker.py — Mask env values for safe display or logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from envdiff.redactor import is_sensitive

_DEFAULT_MASK = "***"
_DEFAULT_PARTIAL_VISIBLE = 2


@dataclass
class MaskResult:
    source: str
    masked: Dict[str, str]
    mask_count: int

    @property
    def has_masked(self) -> bool:
        return self.mask_count > 0

    def summary(self) -> str:
        if not self.has_masked:
            return f"{self.source}: no values masked"
        return f"{self.source}: {self.mask_count} value(s) masked"


def mask_value(
    key: str,
    value: str,
    extra_sensitive: Optional[list] = None,
    partial: bool = False,
    visible_chars: int = _DEFAULT_PARTIAL_VISIBLE,
    mask: str = _DEFAULT_MASK,
) -> str:
    """Return a masked version of *value* if *key* is considered sensitive."""
    sensitive = is_sensitive(key, extra_sensitive or [])
    if not sensitive:
        return value
    if partial and len(value) > visible_chars:
        return value[:visible_chars] + mask
    return mask


def mask_env(
    env: Dict[str, str],
    source: str = "<env>",
    extra_sensitive: Optional[list] = None,
    partial: bool = False,
    visible_chars: int = _DEFAULT_PARTIAL_VISIBLE,
    mask: str = _DEFAULT_MASK,
) -> MaskResult:
    """Return a :class:`MaskResult` with sensitive values replaced."""
    masked: Dict[str, str] = {}
    count = 0
    for key, value in env.items():
        new_val = mask_value(
            key, value,
            extra_sensitive=extra_sensitive,
            partial=partial,
            visible_chars=visible_chars,
            mask=mask,
        )
        masked[key] = new_val
        if new_val != value:
            count += 1
    return MaskResult(source=source, masked=masked, mask_count=count)


def mask_env_file(
    path: str,
    extra_sensitive: Optional[list] = None,
    partial: bool = False,
    visible_chars: int = _DEFAULT_PARTIAL_VISIBLE,
    mask: str = _DEFAULT_MASK,
) -> MaskResult:
    """Parse *path* and return a :class:`MaskResult`."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return mask_env(
        env,
        source=path,
        extra_sensitive=extra_sensitive,
        partial=partial,
        visible_chars=visible_chars,
        mask=mask,
    )
