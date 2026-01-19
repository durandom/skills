"""Layton CLI - argparse structure with global options."""

import argparse
import sys

from laytonlib import __version__
from laytonlib.formatters import OutputFormatter


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all commands."""
    parser = argparse.ArgumentParser(
        prog="layton",
        description="Personal AI assistant for attention management",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--human",
        action="store_true",
        help="Human-readable output (default is JSON)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include debug information",
    )

    subparsers = parser.add_subparsers(dest="command")

    # doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check system health")
    # Hidden --fix flag (not shown in help, but works)
    doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help=argparse.SUPPRESS,  # Hidden from help
    )

    # config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command")

    # config init
    config_init = config_subparsers.add_parser("init", help="Create default config")
    config_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing config",
    )

    # config show
    config_subparsers.add_parser("show", help="Display current config")

    # config keys
    config_subparsers.add_parser("keys", help="List all config keys")

    # config get
    config_get = config_subparsers.add_parser("get", help="Get a config value")
    config_get.add_argument(
        "key", help="Key in dot notation (e.g., work.schedule.start)"
    )

    # config set
    config_set = config_subparsers.add_parser("set", help="Set a config value")
    config_set.add_argument("key", help="Key in dot notation")
    config_set.add_argument("value", help="Value to set (JSON parsed if valid)")

    # context command
    subparsers.add_parser("context", help="Show temporal context")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0=success, 1=fixable, 2=critical)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Create formatter based on --human flag
    formatter = OutputFormatter(human=args.human, verbose=args.verbose)

    # No-arg default: run doctor
    if args.command is None:
        args.command = "doctor"
        args.fix = False

    # Route to command handlers
    if args.command == "doctor":
        from laytonlib.doctor import run_doctor

        return run_doctor(formatter, fix=getattr(args, "fix", False))

    elif args.command == "config":
        from laytonlib.config import run_config

        # No subcommand default: show
        config_cmd = args.config_command or "show"
        return run_config(
            formatter,
            config_cmd,
            key=getattr(args, "key", None),
            value=getattr(args, "value", None),
            force=getattr(args, "force", False),
        )

    elif args.command == "context":
        from laytonlib.context import run_context

        return run_context(formatter)

    else:
        # Unknown command - shouldn't happen with argparse
        formatter.error("UNKNOWN_COMMAND", f"Unknown command: {args.command}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
