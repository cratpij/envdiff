"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from envdiff.diff import diff_envs
from envdiff.parser import parse_env_file
from envdiff.reporter import print_report
from envdiff.validator import validate_env_file
from envdiff.writer import write_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and highlight missing or mismatched keys.",
    )
    parser.add_argument("left", help="First .env file (e.g. .env.development)")
    parser.add_argument("right", help="Second .env file (e.g. .env.production)")
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv", "markdown"],
        default="text",
        dest="format",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color in text output",
    )
    parser.add_argument(
        "--validate",
        metavar="TEMPLATE",
        default=None,
        help="Validate LEFT against a template .env file",
    )
    parser.add_argument(
        "--no-extra",
        action="store_true",
        default=False,
        help="When validating, treat extra keys as errors",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:  # noqa: D401
    """Entry point; returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- optional validation mode -------------------------------------------
    if args.validate:
        try:
            result = validate_env_file(
                args.left,
                args.validate,
                allow_extra=not args.no_extra,
            )
        except FileNotFoundError as exc:
            print(f"envdiff: error: {exc}", file=sys.stderr)
            return 2
        print(result.summary())
        return 0 if result.is_valid else 1

    # --- diff mode (default) -------------------------------------------------
    try:
        left_env = parse_env_file(args.left)
        right_env = parse_env_file(args.right)
    except FileNotFoundError as exc:
        print(f"envdiff: error: {exc}", file=sys.stderr)
        return 2

    diff_result = diff_envs(left_env, right_env, args.left, args.right)

    if args.format == "text":
        print_report(diff_result, use_color=not args.no_color)
    else:
        write_export(diff_result, fmt=args.format, output_path=args.output)

    return 1 if diff_result.has_differences() else 0


if __name__ == "__main__":
    sys.exit(main())
