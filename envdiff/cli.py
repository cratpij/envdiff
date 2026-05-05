"""Command-line interface for envdiff."""

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.diff import diff_envs
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and highlight missing or mismatched keys.",
    )
    parser.add_argument(
        "left",
        metavar="FILE1",
        help="Path to the first .env file (e.g. .env.development)",
    )
    parser.add_argument(
        "right",
        metavar="FILE2",
        help="Path to the second .env file (e.g. .env.production)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found (useful for CI)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI. Returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        left_env = parse_env_file(args.left)
    except FileNotFoundError as exc:
        print(f"envdiff: error: {exc}", file=sys.stderr)
        return 2

    try:
        right_env = parse_env_file(args.right)
    except FileNotFoundError as exc:
        print(f"envdiff: error: {exc}", file=sys.stderr)
        return 2

    result = diff_envs(
        left_env,
        right_env,
        left_label=args.left,
        right_label=args.right,
    )

    print_report(result, color=not args.no_color)

    if args.exit_code and result.has_differences():
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
