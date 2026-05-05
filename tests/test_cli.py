"""Tests for the envdiff CLI module."""

import pytest
from unittest.mock import patch, MagicMock

from envdiff.cli import build_parser, main
from envdiff.diff import EnvDiffResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _no_diff_result():
    return EnvDiffResult(
        left_label="a",
        right_label="b",
        missing_in_right=[],
        missing_in_left=[],
        mismatched={},
    )


def _diff_result():
    return EnvDiffResult(
        left_label="a",
        right_label="b",
        missing_in_right=["SECRET"],
        missing_in_left=[],
        mismatched={},
    )


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

def test_build_parser_requires_two_positional_args():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([".env.dev", ".env.prod"])
    assert args.left == ".env.dev"
    assert args.right == ".env.prod"
    assert args.no_color is False
    assert args.exit_code is False


def test_build_parser_flags():
    parser = build_parser()
    args = parser.parse_args([".env.dev", ".env.prod", "--no-color", "--exit-code"])
    assert args.no_color is True
    assert args.exit_code is True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

@patch("envdiff.cli.print_report")
@patch("envdiff.cli.diff_envs", return_value=_no_diff_result())
@patch("envdiff.cli.parse_env_file", return_value={})
def test_main_returns_zero_when_no_differences(mock_parse, mock_diff, mock_print):
    code = main([".env.dev", ".env.prod"])
    assert code == 0
    assert mock_parse.call_count == 2
    mock_print.assert_called_once()


@patch("envdiff.cli.print_report")
@patch("envdiff.cli.diff_envs", return_value=_diff_result())
@patch("envdiff.cli.parse_env_file", return_value={})
def test_main_returns_zero_without_exit_code_flag(mock_parse, mock_diff, mock_print):
    """Differences found but --exit-code not set → still return 0."""
    code = main([".env.dev", ".env.prod"])
    assert code == 0


@patch("envdiff.cli.print_report")
@patch("envdiff.cli.diff_envs", return_value=_diff_result())
@patch("envdiff.cli.parse_env_file", return_value={})
def test_main_returns_one_with_exit_code_flag_and_differences(mock_parse, mock_diff, mock_print):
    code = main([".env.dev", ".env.prod", "--exit-code"])
    assert code == 1


@patch("envdiff.cli.parse_env_file", side_effect=FileNotFoundError("File not found: .env.missing"))
def test_main_returns_two_when_left_file_missing(mock_parse):
    code = main([".env.missing", ".env.prod"])
    assert code == 2


@patch("envdiff.cli.parse_env_file")
def test_main_returns_two_when_right_file_missing(mock_parse):
    mock_parse.side_effect = [{}] + [FileNotFoundError("File not found: .env.missing")]
    code = main([".env.dev", ".env.missing"])
    assert code == 2


@patch("envdiff.cli.print_report")
@patch("envdiff.cli.diff_envs", return_value=_no_diff_result())
@patch("envdiff.cli.parse_env_file", return_value={})
def test_main_passes_no_color_flag(mock_parse, mock_diff, mock_print):
    main([".env.dev", ".env.prod", "--no-color"])
    _, kwargs = mock_print.call_args
    assert kwargs.get("color") is False
