"""AST-based symbol extraction from Python source files."""

import ast
from pathlib import Path

from .models import ExtractedSymbol, SymbolKind


def _format_annotation(annotation: ast.expr | None) -> str:
    """Format a type annotation node as a string."""
    if annotation is None:
        return ""
    return ast.unparse(annotation)


def _format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Format function/method signature as a string.

    Returns signature like: "(a: float, b: float) -> float"
    """
    args = node.args
    parts = []

    # Handle positional-only args (before /)
    for i, arg in enumerate(args.posonlyargs):
        annotation = _format_annotation(arg.annotation)
        if annotation:
            parts.append(f"{arg.arg}: {annotation}")
        else:
            parts.append(arg.arg)

    # Handle regular args
    # Calculate where defaults start (they align to the end of args list)
    num_args = len(args.args)
    num_defaults = len(args.defaults)
    default_offset = num_args - num_defaults

    for i, arg in enumerate(args.args):
        annotation = _format_annotation(arg.annotation)

        # Check if this arg has a default
        default_idx = i - default_offset
        if default_idx >= 0 and default_idx < len(args.defaults):
            default = ast.unparse(args.defaults[default_idx])
            if annotation:
                parts.append(f"{arg.arg}: {annotation} = {default}")
            else:
                parts.append(f"{arg.arg}={default}")
        else:
            if annotation:
                parts.append(f"{arg.arg}: {annotation}")
            else:
                parts.append(arg.arg)

    # Handle *args
    if args.vararg:
        annotation = _format_annotation(args.vararg.annotation)
        if annotation:
            parts.append(f"*{args.vararg.arg}: {annotation}")
        else:
            parts.append(f"*{args.vararg.arg}")
    elif args.kwonlyargs:
        parts.append("*")  # Separator for keyword-only args

    # Handle keyword-only args
    for i, arg in enumerate(args.kwonlyargs):
        annotation = _format_annotation(arg.annotation)
        default = args.kw_defaults[i]
        if default is not None:
            default_str = ast.unparse(default)
            if annotation:
                parts.append(f"{arg.arg}: {annotation} = {default_str}")
            else:
                parts.append(f"{arg.arg}={default_str}")
        else:
            if annotation:
                parts.append(f"{arg.arg}: {annotation}")
            else:
                parts.append(arg.arg)

    # Handle **kwargs
    if args.kwarg:
        annotation = _format_annotation(args.kwarg.annotation)
        if annotation:
            parts.append(f"**{args.kwarg.arg}: {annotation}")
        else:
            parts.append(f"**{args.kwarg.arg}")

    sig = f"({', '.join(parts)})"

    # Add return annotation
    if node.returns:
        sig += f" -> {_format_annotation(node.returns)}"

    return sig


def extract_symbols(source_path: Path) -> list[ExtractedSymbol]:
    """Extract all classes, functions, and methods from a Python file.

    Args:
        source_path: Path to the Python file.

    Returns:
        List of ExtractedSymbol objects with docstrings and signatures.
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
                    docstring=ast.get_docstring(node),
                    signature=_format_signature(node),
                )
            )
        elif isinstance(node, ast.ClassDef):
            symbols.append(
                ExtractedSymbol(
                    name=node.name,
                    kind=SymbolKind.CLASS,
                    line=node.lineno,
                    parent=None,
                    docstring=ast.get_docstring(node),
                    signature=None,  # Classes don't have signatures
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
                            docstring=ast.get_docstring(child),
                            signature=_format_signature(child),
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
