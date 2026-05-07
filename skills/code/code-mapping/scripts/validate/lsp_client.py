"""LSP client module for Python symbol validation.

Uses Python's ast module for symbol discovery instead of a full LSP server.
This is simpler and sufficient for validating code references in documentation.
"""

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Symbol:
    """Represents a code symbol with its location."""

    name: str
    line: int
    kind: str  # "function", "class", "method"


def get_symbols(file_path: Path) -> list[Symbol]:
    """Extract all symbols from a Python file.

    Args:
        file_path: Path to the Python file.

    Returns:
        List of Symbol objects found in the file.
    """
    if not file_path.exists():
        return []

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    symbols = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if it's a method (inside a class)
            kind = "function"
            symbols.append(Symbol(name=node.name, line=node.lineno, kind=kind))

        elif isinstance(node, ast.ClassDef):
            symbols.append(Symbol(name=node.name, line=node.lineno, kind="class"))

    return symbols


def symbol_exists(file_path: Path, symbol_name: str) -> bool:
    """Check if a symbol exists in a Python file.

    Args:
        file_path: Path to the Python file.
        symbol_name: Name of the symbol to find.

    Returns:
        True if the symbol exists, False otherwise.
    """
    symbols = get_symbols(file_path)
    return any(s.name == symbol_name for s in symbols)


def symbol_at_line(
    file_path: Path, symbol_name: str, line: int, tolerance: int = 0
) -> bool:
    """Check if a symbol exists at or near a specific line.

    Args:
        file_path: Path to the Python file.
        symbol_name: Name of the symbol to find.
        line: Expected line number.
        tolerance: Allow +/- this many lines of drift.

    Returns:
        True if the symbol exists within tolerance of the specified line.
    """
    symbols = get_symbols(file_path)

    for s in symbols:
        if s.name == symbol_name:
            if abs(s.line - line) <= tolerance:
                return True

    return False
