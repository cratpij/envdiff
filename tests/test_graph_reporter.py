"""Tests for envdiff.graph_reporter."""
import io
from envdiff.differ_graph import build_diff_graph
from envdiff.graph_reporter import format_graph_report, print_graph_report


def _graph():
    return build_diff_graph({
        "dev": {"DB_HOST": "localhost", "DEBUG": "true", "SECRET": "dev"},
        "prod": {"DB_HOST": "prod.db", "DEBUG": "true", "PORT": "443"},
    })


def test_format_includes_header():
    report = format_graph_report(_graph(), filename="test.env", color=False)
    assert "Diff Graph" in report
    assert "test.env" in report


def test_format_shows_sources():
    report = format_graph_report(_graph(), color=False)
    assert "dev" in report
    assert "prod" in report


def test_format_shows_mismatch_label():
    report = format_graph_report(_graph(), color=False)
    assert "MISMATCH" in report
    assert "DB_HOST" in report


def test_format_shows_ok_label_for_consistent_key():
    report = format_graph_report(_graph(), color=False)
    assert "OK" in report
    assert "DEBUG" in report


def test_format_shows_missing_label():
    report = format_graph_report(_graph(), color=False)
    assert "MISSING" in report


def test_format_no_filename():
    report = format_graph_report(_graph(), color=False)
    assert "Diff Graph" in report


def test_format_mismatch_shows_per_source_values():
    report = format_graph_report(_graph(), color=False)
    assert "localhost" in report
    assert "prod.db" in report


def test_format_summary_line_present():
    report = format_graph_report(_graph(), color=False)
    assert "source" in report


def test_print_graph_report_writes_to_file():
    buf = io.StringIO()
    print_graph_report(_graph(), filename="x.env", color=False, file=buf)
    output = buf.getvalue()
    assert "Diff Graph" in output
    assert "x.env" in output


def test_format_color_disabled_no_escape_codes():
    report = format_graph_report(_graph(), color=False)
    assert "\033[" not in report


def test_format_all_consistent_no_mismatch_label():
    graph = build_diff_graph({"a": {"FOO": "bar"}, "b": {"FOO": "bar"}})
    report = format_graph_report(graph, color=False)
    assert "MISMATCH" not in report
    assert "OK" in report
