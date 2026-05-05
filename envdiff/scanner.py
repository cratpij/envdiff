"""Scan directories for .env files and batch-profile or diff them."""

import os
from typing import List, Dict, Optional

from envdiff.profiler import EnvProfile, profile_env_file
from envdiff.diff import EnvDiffResult, diff_envs
from envdiff.parser import parse_env_file


DEFAULT_PATTERNS = (".env", ".env.local", ".env.production", ".env.staging", ".env.test")


def find_env_files(
    directory: str,
    patterns: tuple = DEFAULT_PATTERNS,
    recursive: bool = False,
) -> List[str]:
    """Find .env files in a directory matching given filename patterns."""
    found: List[str] = []
    if recursive:
        for root, _dirs, files in os.walk(directory):
            for name in files:
                if name in patterns or any(name.endswith(p) for p in patterns):
                    found.append(os.path.join(root, name))
    else:
        for name in os.listdir(directory):
            if name in patterns or any(name.endswith(p) for p in patterns):
                full = os.path.join(directory, name)
                if os.path.isfile(full):
                    found.append(full)
    return sorted(found)


def scan_and_profile(
    directory: str,
    patterns: tuple = DEFAULT_PATTERNS,
    recursive: bool = False,
) -> Dict[str, EnvProfile]:
    """Find and profile all .env files in a directory."""
    paths = find_env_files(directory, patterns=patterns, recursive=recursive)
    return {path: profile_env_file(path) for path in paths}


def scan_and_diff_all(
    directory: str,
    baseline: str,
    patterns: tuple = DEFAULT_PATTERNS,
    recursive: bool = False,
) -> Dict[str, Optional[EnvDiffResult]]:
    """
    Diff every discovered .env file against a baseline file.
    Returns a mapping of path -> EnvDiffResult (or None if baseline missing).
    """
    if not os.path.isfile(baseline):
        raise FileNotFoundError(f"Baseline file not found: {baseline}")

    baseline_env = parse_env_file(baseline)
    paths = find_env_files(directory, patterns=patterns, recursive=recursive)
    results: Dict[str, Optional[EnvDiffResult]] = {}
    for path in paths:
        if os.path.abspath(path) == os.path.abspath(baseline):
            continue
        other_env = parse_env_file(path)
        results[path] = diff_envs(baseline_env, other_env)
    return results
