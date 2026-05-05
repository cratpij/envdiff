"""Tests for envdiff.patcher."""

from __future__ import annotations

import pytest

from envdiff.diff import EnvDiffResult, diff_envs
from envdiff.patcher import patch_env, patch_env_files, patch_env_to_string


def _result(base, donor) -> EnvDiffResult:
    return diff_envs(base, donor)


def test_patch_env_adds_missing_keys():
    base = {"HOST": "localhost"}
    donor = {"HOST": "localhost", "PORT": "5432"}
    result = _result(base, donor)
    patched = patch_env(base, donor, result)
    assert patched["PORT"] == "5432"
    assert patched["HOST"] == "localhost"


def test_patch_env_does_not_overwrite_by_default():
    base = {"HOST": "localhost"}
    donor = {"HOST": "remotehost"}
    result = _result(base, donor)
    patched = patch_env(base, donor, result)
    assert patched["HOST"] == "localhost"


def test_patch_env_overwrite_mismatched():
    base = {"HOST": "localhost"}
    donor = {"HOST": "remotehost"}
    result = _result(base, donor)
    patched = patch_env(base, donor, result, overwrite_mismatched=True)
    assert patched["HOST"] == "remotehost"


def test_patch_env_uses_placeholder_for_empty_donor_value():
    base = {}
    donor = {"NEW_KEY": ""}
    result = _result(base, donor)
    patched = patch_env(base, donor, result, placeholder="REPLACE_ME")
    assert patched["NEW_KEY"] == "REPLACE_ME"


def test_patch_env_does_not_modify_original():
    base = {"A": "1"}
    donor = {"A": "1", "B": "2"}
    result = _result(base, donor)
    patch_env(base, donor, result)
    assert "B" not in base


def test_patch_env_to_string_marks_added():
    patched = {"HOST": "localhost", "PORT": "5432"}
    output = patch_env_to_string(patched, added_keys=["PORT"])
    assert "PORT=5432  # PATCHED" in output
    assert "HOST=localhost" in output
    assert "# PATCHED" not in output.split("PORT")[0]


def test_patch_env_to_string_marks_overwritten():
    patched = {"HOST": "remotehost"}
    output = patch_env_to_string(patched, added_keys=[], overwritten_keys=["HOST"])
    assert "HOST=remotehost  # PATCHED" in output


def test_patch_env_to_string_sorted_keys():
    patched = {"Z": "z", "A": "a", "M": "m"}
    lines = patch_env_to_string(patched, added_keys=[]).splitlines()
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)


def test_patch_env_files(tmp_path):
    base = tmp_path / ".env.base"
    donor = tmp_path / ".env.donor"
    base.write_text("HOST=localhost\n")
    donor.write_text("HOST=localhost\nPORT=5432\nDEBUG=false\n")

    output = patch_env_files(str(base), str(donor))
    assert "PORT=5432  # PATCHED" in output
    assert "DEBUG=false  # PATCHED" in output
    assert "HOST=localhost" in output


def test_patch_env_files_overwrite_mismatched(tmp_path):
    base = tmp_path / ".env.base"
    donor = tmp_path / ".env.donor"
    base.write_text("HOST=localhost\n")
    donor.write_text("HOST=remotehost\n")

    output = patch_env_files(str(base), str(donor), overwrite_mismatched=True)
    assert "HOST=remotehost  # PATCHED" in output
