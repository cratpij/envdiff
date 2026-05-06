"""Audit env files by combining lint, profile, validation, and score results."""

from dataclasses import dataclass, field
from typing import Optional

from envdiff.linter import LintResult, lint_env_file
from envdiff.profiler import EnvProfile, profile_env_file
from envdiff.validator import ValidationResult, validate_env_file
from envdiff.scorer import EnvScore, score_env


@dataclass
class AuditResult:
    path: str
    lint: LintResult
    profile: EnvProfile
    validation: ValidationResult
    score: EnvScore
    notes: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            not self.lint.has_errors()
            and self.validation.is_valid()
            and self.score.is_healthy()
        )

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"[{status}] {self.path} | "
            f"Score: {self.score.score:.0f} ({self.score.grade()}) | "
            f"Lint errors: {sum(1 for i in self.lint.issues if i.level == 'error')} | "
            f"Validation: {'ok' if self.validation.is_valid() else 'issues found'}"
        )


def audit_env_file(
    path: str,
    required_keys: Optional[list] = None,
    allowed_keys: Optional[list] = None,
) -> AuditResult:
    """Run a full audit on a single .env file."""
    lint = lint_env_file(path)
    profile = profile_env_file(path)
    validation = validate_env_file(
        path,
        required_keys=required_keys or [],
        allowed_keys=allowed_keys,
    )
    score = score_env(profile=profile, lint=lint, validation=validation)
    notes = []
    if profile.total_keys == 0:
        notes.append("File is empty or has no valid key-value pairs.")
    return AuditResult(
        path=path,
        lint=lint,
        profile=profile,
        validation=validation,
        score=score,
        notes=notes,
    )
