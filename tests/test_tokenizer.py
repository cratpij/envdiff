"""Tests for envdiff.tokenizer and envdiff.tokenizer_reporter."""
from __future__ import annotations

import pytest

from envdiff.tokenizer import (
    TokenType,
    tokenize,
    tokenize_file,
)
from envdiff.tokenizer_reporter import format_tokenize_report


# ---------------------------------------------------------------------------
# tokenize()
# ---------------------------------------------------------------------------

def test_tokenize_empty_string():
    result = tokenize("")
    assert result.tokens == []
    assert result.assignments == []


def test_tokenize_blank_line():
    result = tokenize("\n")
    assert len(result.tokens) == 1
    assert result.tokens[0].token_type == TokenType.BLANK


def test_tokenize_comment_line():
    result = tokenize("# a comment")
    assert len(result.comments) == 1
    assert result.comments[0].raw == "# a comment"


def test_tokenize_simple_assignment():
    result = tokenize("FOO=bar")
    assert len(result.assignments) == 1
    tok = result.assignments[0]
    assert tok.key == "FOO"
    assert tok.value == "bar"
    assert tok.line_number == 1


def test_tokenize_quoted_value():
    result = tokenize('DB_URL="postgres://localhost"')
    tok = result.assignments[0]
    assert tok.value == "postgres://localhost"


def test_tokenize_single_quoted_value():
    result = tokenize("SECRET='abc123'")
    tok = result.assignments[0]
    assert tok.value == "abc123"


def test_tokenize_malformed_line():
    result = tokenize("THIS_IS_NOT_VALID")
    assert len(result.malformed) == 1
    assert result.malformed[0].raw == "THIS_IS_NOT_VALID"


def test_tokenize_mixed_content():
    content = "# header\nFOO=1\n\nBAR=2\nBAD_LINE\n"
    result = tokenize(content, source="test.env")
    assert len(result.assignments) == 2
    assert len(result.comments) == 1
    assert len(result.malformed) == 1
    assert result.source == "test.env"


def test_tokenize_line_numbers():
    content = "# comment\nKEY=val\nBAD"
    result = tokenize(content)
    assert result.tokens[0].line_number == 1
    assert result.tokens[1].line_number == 2
    assert result.tokens[2].line_number == 3


def test_summary_no_malformed():
    result = tokenize("A=1\nB=2\n# note")
    assert "2 assignments" in result.summary()
    assert "1 comments" in result.summary()
    assert "0 malformed" in result.summary()


def test_is_assignment_property():
    result = tokenize("X=10")
    assert result.assignments[0].is_assignment is True
    assert result.assignments[0].is_comment is False
    assert result.assignments[0].is_malformed is False


def test_tokenize_file_reads_content(tmp_path):
    env = tmp_path / ".env"
    env.write_text("HOST=localhost\nPORT=5432\n")
    result = tokenize_file(str(env))
    assert len(result.assignments) == 2
    assert result.source == str(env)


def test_tokenize_file_not_found():
    with pytest.raises(FileNotFoundError):
        tokenize_file("/nonexistent/.env")


# ---------------------------------------------------------------------------
# format_tokenize_report()
# ---------------------------------------------------------------------------

def test_report_includes_header():
    result = tokenize("A=1", source="dev.env")
    report = format_tokenize_report(result, use_color=False)
    assert "dev.env" in report


def test_report_shows_assignment():
    result = tokenize("FOO=bar")
    report = format_tokenize_report(result, filename="x.env", use_color=False)
    assert "FOO" in report
    assert "bar" in report


def test_report_shows_malformed():
    result = tokenize("BADLINE")
    report = format_tokenize_report(result, use_color=False)
    assert "Malformed" in report
    assert "BADLINE" in report


def test_report_no_malformed_section_when_clean():
    result = tokenize("A=1\n# ok")
    report = format_tokenize_report(result, use_color=False)
    assert "Malformed" not in report


def test_report_uses_filename_override():
    result = tokenize("", source="original.env")
    report = format_tokenize_report(result, filename="override.env", use_color=False)
    assert "override.env" in report
    assert "original.env" not in report
