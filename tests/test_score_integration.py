"""Integration tests: scorer + profiler + linter + validator."""
import textwrap
import tempfile
import os

from envdiff.profiler import profile_env_file
from envdiff.linter import lint_lines
from envdiff.validator import validate_env_file
from envdiff.scorer import compute_score
from envdiff.score_reporter import format_score_report


def _write(tmp_path, name, content):
    p = os.path.join(tmp_path, name)
    with open(p, "w") as f:
        f.write(textwrap.dedent(content))
    return p


def test_healthy_env_scores_high(tmp_path):
    path = _write(tmp_path, ".env", """
        DB_HOST=localhost
        DB_PORT=5432
        SECRET_KEY=supersecretvalue
    """)
    profile = profile_env_file(path)
    with open(path) as f:
        lines = f.readlines()
    lint = lint_lines(lines)
    validation = validate_env_file(path, required_keys=["DB_HOST", "DB_PORT"])
    score = compute_score(path, profile, lint, validation)
    assert score.score >= 75
    assert score.grade in ("A", "B")


def test_env_with_empty_values_scores_lower(tmp_path):
    path = _write(tmp_path, ".env", """
        DB_HOST=
        DB_PORT=
        SECRET_KEY=
    """)
    profile = profile_env_file(path)
    with open(path) as f:
        lines = f.readlines()
    lint = lint_lines(lines)
    validation = validate_env_file(path, required_keys=[])
    score = compute_score(path, profile, lint, validation)
    assert score.score < 100
    assert "empty_values" in score.deductions


def test_env_missing_required_keys_penalised(tmp_path):
    path = _write(tmp_path, ".env", """
        DB_HOST=localhost
    """)
    profile = profile_env_file(path)
    with open(path) as f:
        lines = f.readlines()
    lint = lint_lines(lines)
    validation = validate_env_file(
        path, required_keys=["DB_HOST", "DB_PORT", "SECRET_KEY"]
    )
    score = compute_score(path, profile, lint, validation)
    assert "missing_required" in score.deductions
    assert score.score < 90


def test_format_report_integration(tmp_path):
    path = _write(tmp_path, ".env", "KEY=value\n")
    profile = profile_env_file(path)
    with open(path) as f:
        lines = f.readlines()
    lint = lint_lines(lines)
    validation = validate_env_file(path, required_keys=[])
    score = compute_score(path, profile, lint, validation)
    report = format_score_report(score, use_color=False)
    assert str(score.score) in report
    assert score.grade in report
