"""Data models for code map generation."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SymbolKind(Enum):
    """Type of code symbol."""

    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"


@dataclass
class ExtractedSymbol:
    """Symbol extracted from source code via AST."""

    name: str
    kind: SymbolKind
    line: int
    parent: str | None = None  # For methods: parent class name
    docstring: str | None = None  # Extracted docstring
    signature: str | None = (
        None  # Formatted signature (e.g., "(a: float, b: float) -> float")
    )


@dataclass
class Section:
    """A section in a map file documenting a symbol."""

    symbol_name: str
    symbol_kind: SymbolKind
    line_number: int
    description: str
    is_placeholder: bool


@dataclass
class MapFile:
    """Represents a single map markdown file."""

    source_path: Path  # Relative path to source file
    map_path: Path  # Relative path to map file
    file_description: str
    file_description_is_placeholder: bool
    sections: list[Section] = field(default_factory=list)


@dataclass
class MissingDocstring:
    """A symbol missing a docstring in source code."""

    source_path: Path  # Relative to src_dir
    line: int
    symbol_name: str


@dataclass
class ChangeReport:
    """Report of changes made during map generation."""

    created_files: list[Path] = field(default_factory=list)
    updated_files: list[Path] = field(default_factory=list)
    deleted_files: list[Path] = field(default_factory=list)
    new_sections: list[tuple[Path, str]] = field(default_factory=list)  # (file, symbol)
    removed_sections: list[tuple[Path, str]] = field(
        default_factory=list
    )  # (file, symbol)
    missing_docstrings: list[MissingDocstring] = field(
        default_factory=list
    )  # Source symbols without docstrings
    missing_descriptions: list[Path] = field(
        default_factory=list
    )  # Map files needing manual descriptions (project, domain)
