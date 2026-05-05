"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from envdiff.diff import diff_envs, has_differences
from envdiff.exporter import OutputFormat
from envdiff.parser import parse_env_file
from envdiff.reporter import print_report
from envdiff.writer import write_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    parser.add_argument("left", help="First .env file (reference)")
    parser.add_argument("right", help="Second .env file (target)")
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    parser.add_argument(
        "--export",
        metavar="FORMAT",
        choices=["json", "csv", "markdown"],
        default=None,
        help="Export diff in the given format (json, csv, markdown)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write export output to FILE instead of stdout",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point.  Returns an exit code (0 = no diff, 1 = diff found)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        left_env = parse_env_file(args.left)
        right_env = parse_env_file(args.right)
    except FileNotFoundError as exc:
        print(f"envdiff: error: {exc}", file=sys.stderr)
        return 2

    result = diff_envs(left_env, right_env)

    if args.export:
        write_export(result, args.export, args.output)  # type: ignore[arg-type]
    else:
        print_report(result, use_color=not args.no_color)

    return 1 if has_differences(result) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
