"""Score .env files for overall health and completeness."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.profiler import EnvProfile
from envdiff.linter import LintResult
from envdiff.validator import ValidationResult


@dataclass
class EnvScore:
    """Aggregated health score for a single .env file."""
    path: str
    total: int = 100
    deductions: Dict[str, int] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    @property
    def score(self) -> int:
        return max(0, self.total - sum(self.deductions.values()))

    @property
    def grade(self) -> str:
        s = self.score
        if s >= 90:
            return "A"
        if s >= 75:
            return "B"
        if s >= 60:
            return "C"
        if s >= 40:
            return "D"
        return "F"

    def is_healthy(self) -> bool:
        return self.score >= 75


def score_from_profile(score: EnvScore, profile: EnvProfile) -> None:
    """Apply deductions based on profiler findings."""
    if profile.empty_value_keys:
        penalty = min(20, len(profile.empty_value_keys) * 4)
        score.deductions["empty_values"] = penalty
        score.notes.append(
            f"{len(profile.empty_value_keys)} key(s) have empty values (-{penalty})"
        )
    if profile.long_value_keys:
        penalty = min(10, len(profile.long_value_keys) * 2)
        score.deductions["long_values"] = penalty
        score.notes.append(
            f"{len(profile.long_value_keys)} key(s) have unusually long values (-{penalty})"
        )


def score_from_lint(score: EnvScore, lint: LintResult) -> None:
    """Apply deductions based on lint findings."""
    errors = [i for i in lint.issues if i.severity == "error"]
    warnings = [i for i in lint.issues if i.severity == "warning"]
    if errors:
        penalty = min(40, len(errors) * 8)
        score.deductions["lint_errors"] = penalty
        score.notes.append(f"{len(errors)} lint error(s) (-{penalty})")
    if warnings:
        penalty = min(15, len(warnings) * 3)
        score.deductions["lint_warnings"] = penalty
        score.notes.append(f"{len(warnings)} lint warning(s) (-{penalty})")


def score_from_validation(score: EnvScore, validation: ValidationResult) -> None:
    """Apply deductions based on validation findings."""
    if validation.missing_required:
        penalty = min(30, len(validation.missing_required) * 6)
        score.deductions["missing_required"] = penalty
        score.notes.append(
            f"{len(validation.missing_required)} required key(s) missing (-{penalty})"
        )


def compute_score(
    path: str,
    profile: EnvProfile,
    lint: LintResult,
    validation: ValidationResult,
) -> EnvScore:
    """Compute a composite health score for a .env file."""
    score = EnvScore(path=path)
    score_from_profile(score, profile)
    score_from_lint(score, lint)
    score_from_validation(score, validation)
    return score
