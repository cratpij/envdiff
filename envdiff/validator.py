"""Validator module for envdiff — validate .env files against a schema or template."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envdiff.parser import parse_env_file


@dataclass
class ValidationResult:
    """Holds the outcome of validating an env file against a template."""

    missing_required: List[str] = field(default_factory=list)
    extra_keys: List[str] = field(default_factory=list)
    empty_values: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True only when there are no missing required keys."""
        return len(self.missing_required) == 0

    def summary(self) -> str:
        parts: List[str] = []
        if self.missing_required:
            parts.append(f"Missing required keys ({len(self.missing_required)}): {', '.join(sorted(self.missing_required))}")
        if self.extra_keys:
            parts.append(f"Extra keys ({len(self.extra_keys)}): {', '.join(sorted(self.extra_keys))}")
        if self.empty_values:
            parts.append(f"Empty values ({len(self.empty_values)}): {', '.join(sorted(self.empty_values))}")
        return "\n".join(parts) if parts else "All required keys present."


def validate_env(
    env: Dict[str, str],
    template: Dict[str, str],
    *,
    allow_extra: bool = True,
    flag_empty: bool = True,
) -> ValidationResult:
    """Validate *env* against a *template* mapping.

    Parameters
    ----------
    env:          The parsed env mapping to validate.
    template:     The reference template (keys are required; values are ignored).
    allow_extra:  When False, keys present in *env* but absent from *template*
                  are reported in ``extra_keys``.
    flag_empty:   When True, keys whose value is an empty string are reported.
    """
    required: Set[str] = set(template.keys())
    actual: Set[str] = set(env.keys())

    missing_required = sorted(required - actual)
    extra_keys = sorted(actual - required) if not allow_extra else []
    empty_values = sorted(k for k in actual if flag_empty and env[k] == "")

    return ValidationResult(
        missing_required=missing_required,
        extra_keys=extra_keys,
        empty_values=empty_values,
    )


def validate_env_file(
    env_path: str,
    template_path: str,
    *,
    allow_extra: bool = True,
    flag_empty: bool = True,
) -> ValidationResult:
    """Parse both files from disk and delegate to :func:`validate_env`."""
    env = parse_env_file(env_path)
    template = parse_env_file(template_path)
    return validate_env(env, template, allow_extra=allow_extra, flag_empty=flag_empty)
