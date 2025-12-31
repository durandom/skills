"""AST-based symbol extraction from Python source files."""

import ast
from pathlib import Path

from .models import ExtractedSymbol, SymbolKind


def extract_symbols(source_path: Path) -> list[ExtractedSymbol]:
    """Extract all classes, functions, and methods from a Python file.

    Args:
        source_path: Path to the Python file.

    Returns:
        List of ExtractedSymbol objects. Methods include their parent class name.
    """
    if not source_path.exists():
        return []

    try:
        source = source_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    symbols = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            symbols.append(
                ExtractedSymbol(
                    name=node.name,
                    kind=SymbolKind.FUNCTION,
                    line=node.lineno,
                    parent=None,
                )
            )
        elif isinstance(node, ast.ClassDef):
            symbols.append(
                ExtractedSymbol(
                    name=node.name,
                    kind=SymbolKind.CLASS,
                    line=node.lineno,
                    parent=None,
                )
            )
            # Extract methods from the class
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                    symbols.append(
                        ExtractedSymbol(
                            name=child.name,
                            kind=SymbolKind.METHOD,
                            line=child.lineno,
                            parent=node.name,
                        )
                    )

    return symbols


def extract_module_docstring(source_path: Path) -> str | None:
    """Extract module-level docstring if present.

    Args:
        source_path: Path to the Python file.

    Returns:
        The module docstring, or None if not present.
    """
    if not source_path.exists():
        return None

    try:
        source = source_path.read_text()
        tree = ast.parse(source)
        return ast.get_docstring(tree)
    except (SyntaxError, UnicodeDecodeError):
        return None
