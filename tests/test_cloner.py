"""Tests for envdiff.cloner."""

import os
import pytest

from envdiff.cloner import CloneResult, clone_env, clone_env_file


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123", "DEBUG": "true"}


# ---------------------------------------------------------------------------
# CloneResult helpers
# ---------------------------------------------------------------------------

def test_total_cloned():
    result = CloneResult(source_path="a", dest_path="b", cloned={"A": "1", "B": "2"})
    assert result.total_cloned() == 2


def test_summary_basic():
    result = CloneResult(source_path=".env.dev", dest_path=".env.prod", cloned={"A": "1"})
    assert ".env.dev" in result.summary()
    assert ".env.prod" in result.summary()
    assert "1 key" in result.summary()


def test_summary_with_skipped_and_renamed():
    result = CloneResult(
        source_path="src",
        dest_path="dst",
        cloned={"NEW_KEY": "val"},
        skipped=["SECRET"],
        renamed={"OLD_KEY": "NEW_KEY"},
    )
    s = result.summary()
    assert "Skipped 1" in s
    assert "OLD_KEY->NEW_KEY" in s


# ---------------------------------------------------------------------------
# clone_env
# ---------------------------------------------------------------------------

def test_clone_env_no_filters():
    result = clone_env(ENV_A, "src", "dst")
    assert result.cloned == ENV_A
    assert result.skipped == []
    assert result.renamed == {}


def test_clone_env_include():
    result = clone_env(ENV_A, "src", "dst", include=["DB_HOST", "DB_PORT"])
    assert set(result.cloned.keys()) == {"DB_HOST", "DB_PORT"}
    assert "SECRET_KEY" in result.skipped
    assert "DEBUG" in result.skipped


def test_clone_env_exclude():
    result = clone_env(ENV_A, "src", "dst", exclude=["SECRET_KEY", "DEBUG"])
    assert "SECRET_KEY" not in result.cloned
    assert "DEBUG" not in result.cloned
    assert "DB_HOST" in result.cloned


def test_clone_env_rename():
    result = clone_env(ENV_A, "src", "dst", renames={"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.cloned
    assert "DB_HOST" not in result.cloned
    assert result.cloned["DATABASE_HOST"] == "localhost"
    assert result.renamed == {"DB_HOST": "DATABASE_HOST"}


def test_clone_env_include_and_rename():
    result = clone_env(
        ENV_A, "src", "dst",
        include=["DB_HOST"],
        renames={"DB_HOST": "HOST"},
    )
    assert result.cloned == {"HOST": "localhost"}
    assert result.renamed == {"DB_HOST": "HOST"}


def test_clone_env_empty_source():
    result = clone_env({}, "src", "dst")
    assert result.cloned == {}
    assert result.skipped == []


# ---------------------------------------------------------------------------
# clone_env_file
# ---------------------------------------------------------------------------

def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_clone_env_file_writes_dest(tmp_path):
    src = _write(tmp_path, ".env.src", "FOO=bar\nBAZ=qux\n")
    dst = str(tmp_path / ".env.dst")
    result = clone_env_file(src, dst)
    assert os.path.exists(dst)
    content = open(dst).read()
    assert "FOO=bar" in content
    assert "BAZ=qux" in content
    assert result.total_cloned() == 2


def test_clone_env_file_with_exclude(tmp_path):
    src = _write(tmp_path, ".env.src", "SECRET=abc\nPORT=8080\n")
    dst = str(tmp_path / ".env.dst")
    result = clone_env_file(src, dst, exclude=["SECRET"])
    content = open(dst).read()
    assert "SECRET" not in content
    assert "PORT=8080" in content
    assert "SECRET" in result.skipped
