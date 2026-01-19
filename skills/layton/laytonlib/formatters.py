"""Output formatting for Layton CLI.

JSON is the default output format (agent-first design).
Use --human flag for human-readable output.
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OutputFormatter:
    """Formats CLI output as JSON (default) or human-readable.

    Usage:
        formatter = OutputFormatter(human=args.human)
        formatter.success({"key": "value"}, next_steps=["do this"])
        formatter.error("ERROR_CODE", "Something went wrong")
    """

    human: bool = False
    verbose: bool = False
    _debug_info: dict[str, Any] = field(default_factory=dict)

    def add_debug(self, key: str, value: Any) -> None:
        """Add debug information (included if verbose=True)."""
        self._debug_info[key] = value

    def success(
        self,
        data: dict[str, Any],
        next_steps: list[str] | None = None,
    ) -> None:
        """Output a success response.

        Args:
            data: The response data
            next_steps: Optional list of suggested next actions
        """
        if self.human:
            self._print_human_success(data, next_steps)
        else:
            response = {
                "success": True,
                "data": data,
                "next_steps": next_steps or [],
            }
            if self.verbose and self._debug_info:
                response["debug"] = self._debug_info
            print(json.dumps(response, indent=2))

    def error(
        self,
        code: str,
        message: str,
        next_steps: list[str] | None = None,
    ) -> None:
        """Output an error response.

        Args:
            code: Error code (e.g., CONFIG_MISSING)
            message: Human-readable error message
            next_steps: Optional list of recovery suggestions
        """
        if self.human:
            self._print_human_error(code, message, next_steps)
        else:
            response = {
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                },
                "next_steps": next_steps or [],
            }
            if self.verbose and self._debug_info:
                response["debug"] = self._debug_info
            print(json.dumps(response, indent=2))

    def _print_human_success(
        self,
        data: dict[str, Any],
        next_steps: list[str] | None,
    ) -> None:
        """Print human-readable success output."""
        # Pretty-print the data
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            elif isinstance(value, list):
                print(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            print(f"  {k}: {v}")
                        print()
                    else:
                        print(f"  - {item}")
            else:
                print(f"{key}: {value}")

        if next_steps:
            print()
            print("Next steps:")
            for step in next_steps:
                print(f"  - {step}")

    def _print_human_error(
        self,
        code: str,
        message: str,
        next_steps: list[str] | None,
    ) -> None:
        """Print human-readable error output."""
        print(f"Error [{code}]: {message}", file=sys.stderr)

        if next_steps:
            print()
            print("To fix:")
            for step in next_steps:
                print(f"  - {step}")
