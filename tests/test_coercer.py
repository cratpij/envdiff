"""Tests for envdiff.coercer and envdiff.coercion_reporter."""

import pytest

from envdiff.coercer import (
    CoercionResult,
    _coerce_value,
    coerce_env,
    coerce_env_file,
)
from envdiff.coercion_reporter import format_coercion_report


# ---------------------------------------------------------------------------
# _coerce_value
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["true", "True", "TRUE", "yes", "1", "on"])
def test_coerce_value_true_variants(raw):
    assert _coerce_value(raw) is True


@pytest.mark.parametrize("raw", ["false", "False", "FALSE", "no", "0", "off"])
def test_coerce_value_false_variants(raw):
    assert _coerce_value(raw) is False


def test_coerce_value_integer():
    assert _coerce_value("42") == 42
    assert isinstance(_coerce_value("42"), int)


def test_coerce_value_float():
    result = _coerce_value("3.14")
    assert abs(result - 3.14) < 1e-9
    assert isinstance(result, float)


def test_coerce_value_plain_string():
    assert _coerce_value("hello") == "hello"
    assert isinstance(_coerce_value("hello"), str)


def test_coerce_value_empty_string():
    assert _coerce_value("") == ""


# ---------------------------------------------------------------------------
# coerce_env
# ---------------------------------------------------------------------------

def test_coerce_env_mixed_types():
    env = {"DEBUG": "true", "PORT": "8080", "NAME": "myapp", "RATIO": "0.5"}
    result = coerce_env(env, source="test")
    assert result.coerced["DEBUG"] is True
    assert result.coerced["PORT"] == 8080
    assert result.coerced["NAME"] == "myapp"
    assert abs(result.coerced["RATIO"] - 0.5) < 1e-9


def test_coerce_env_preserves_original():
    env = {"PORT": "9000"}
    result = coerce_env(env)
    assert result.original["PORT"] == "9000"
    assert result.coerced["PORT"] == 9000


def test_coerce_env_changed_keys():
    env = {"A": "1", "B": "hello"}
    result = coerce_env(env)
    assert "A" in result.changed_keys()
    assert "B" not in result.changed_keys()


def test_coerce_env_summary_no_changes():
    result = coerce_env({"NAME": "app"}, source=".env")
    assert "no coercion" in result.summary()


def test_coerce_env_summary_with_changes():
    result = coerce_env({"PORT": "80", "DEBUG": "true"}, source=".env.test")
    summary = result.summary()
    assert "2 key(s) coerced" in summary
    assert "DEBUG" in summary
    assert "PORT" in summary


# ---------------------------------------------------------------------------
# coerce_env_file
# ---------------------------------------------------------------------------

def test_coerce_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=3000\nDEBUG=true\nAPP=myservice\n")
    result = coerce_env_file(str(env_file))
    assert result.coerced["PORT"] == 3000
    assert result.coerced["DEBUG"] is True
    assert result.coerced["APP"] == "myservice"


# ---------------------------------------------------------------------------
# format_coercion_report
# ---------------------------------------------------------------------------

def test_format_report_no_changes():
    result = CoercionResult(source=".env", coerced={"A": "hello"}, original={"A": "hello"})
    report = format_coercion_report(result, color=False)
    assert "nothing coerced" in report


def test_format_report_shows_changed_key():
    result = CoercionResult(
        source=".env",
        coerced={"PORT": 8080},
        original={"PORT": "8080"},
    )
    report = format_coercion_report(result, color=False)
    assert "PORT" in report
    assert "8080" in report
    assert "int" in report


def test_format_report_includes_header():
    result = CoercionResult(source=".env.prod", coerced={}, original={})
    report = format_coercion_report(result, filename="prod.env", color=False)
    assert "prod.env" in report
