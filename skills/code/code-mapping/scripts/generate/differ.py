"""Diff and merge logic for idempotent map updates."""

import re
from dataclasses import dataclass, field
from pathlib import Path

from .models import ExtractedSymbol, MapFile, Section
from .renderer import is_placeholder, make_placeholder

# Pattern to match section headers: ### [`symbol`](path#L42)
SECTION_HEADER_PATTERN = re.compile(r"^###\s+\[`([^`]+)`\]\([^)]+#L(\d+)\)")

# Pattern to match method list items: - [`method`](path#L42): description
METHOD_PATTERN = re.compile(r"^-\s+\[`([^`]+)`\]\([^)]+#L(\d+)\):\s*(.*)$")

# Pattern to match table rows: | [`symbol`](path#L42) | description |
TABLE_ROW_PATTERN = re.compile(
    r"^\|\s*\[`([^`]+)`\]\([^)]+#L(\d+)\)\s*\|\s*(.+?)\s*\|$"
)


@dataclass
class ParsedSection:
    """A section parsed from an existing map file."""

    symbol_name: str
    line_number: int
    description: str
    is_placeholder: bool


@dataclass
class ParsedMapFile:
    """Parsed content from an existing map file."""

    file_description: str
    file_description_is_placeholder: bool
    sections: dict[str, ParsedSection] = field(default_factory=dict)


def parse_existing_map(map_path: Path) -> ParsedMapFile | None:
    """Parse an existing map markdown file to extract sections.

    Args:
        map_path: Path to the map file.

    Returns:
        ParsedMapFile with extracted content, or None if file doesn't exist.
    """
    if not map_path.exists():
        return None

    content = map_path.read_text()
    lines = content.split("\n")

    result = ParsedMapFile(
        file_description="",
        file_description_is_placeholder=True,
    )

    # Parse file description (content after # title until ## section)
    in_description = False
    description_lines = []

    for i, line in enumerate(lines):
        if line.startswith("# ") and not in_description:
            in_description = True
            continue

        if in_description:
            if line.startswith("## "):
                break
            description_lines.append(line)

    file_desc = "\n".join(description_lines).strip()
    result.file_description = file_desc
    result.file_description_is_placeholder = is_placeholder(file_desc)

    # Parse sections
    current_section_name = None
    current_section_line = 0
    current_description_lines = []

    for i, line in enumerate(lines):
        # Check for section header
        header_match = SECTION_HEADER_PATTERN.match(line)
        if header_match:
            # Save previous section if any
            if current_section_name:
                desc = "\n".join(current_description_lines).strip()
                result.sections[current_section_name] = ParsedSection(
                    symbol_name=current_section_name,
                    line_number=current_section_line,
                    description=desc,
                    is_placeholder=is_placeholder(desc),
                )

            current_section_name = header_match.group(1)
            current_section_line = int(header_match.group(2))
            current_description_lines = []
            continue

        # Check for method list item
        method_match = METHOD_PATTERN.match(line)
        if method_match:
            method_name = method_match.group(1)
            method_line = int(method_match.group(2))
            method_desc = method_match.group(3).strip()
            result.sections[method_name] = ParsedSection(
                symbol_name=method_name,
                line_number=method_line,
                description=method_desc,
                is_placeholder=is_placeholder(method_desc),
            )
            continue

        # Check for table row (new format)
        table_match = TABLE_ROW_PATTERN.match(line)
        if table_match:
            symbol_name = table_match.group(1)
            symbol_line = int(table_match.group(2))
            symbol_desc = table_match.group(3).strip()
            result.sections[symbol_name] = ParsedSection(
                symbol_name=symbol_name,
                line_number=symbol_line,
                description=symbol_desc,
                is_placeholder=is_placeholder(symbol_desc),
            )
            continue

        # Collect description lines for current section
        if (
            current_section_name
            and not line.startswith("##")
            and not line.startswith("**")
        ):
            current_description_lines.append(line)

    # Save last section
    if current_section_name:
        desc = "\n".join(current_description_lines).strip()
        result.sections[current_section_name] = ParsedSection(
            symbol_name=current_section_name,
            line_number=current_section_line,
            description=desc,
            is_placeholder=is_placeholder(desc),
        )

    return result


def merge_maps(
    existing: ParsedMapFile | None,
    symbols: list[ExtractedSymbol],
    source_path: Path,
    map_path: Path,
) -> tuple[MapFile, list[str], list[str]]:
    """Merge existing map content with current source symbols.

    Args:
        existing: Parsed existing map file, or None if new.
        symbols: Symbols extracted from current source.
        source_path: Relative path to source file.
        map_path: Relative path to map file.

    Returns:
        Tuple of (merged MapFile, removed symbol names, new symbol names).
    """
    current_names = {s.name for s in symbols}

    if existing is None:
        # First generation - all sections are new with placeholders
        sections = [
            Section(
                symbol_name=s.name,
                symbol_kind=s.kind,
                line_number=s.line,
                description=make_placeholder(f"Describe {s.name}"),
                is_placeholder=True,
            )
            for s in symbols
        ]
        return (
            MapFile(
                source_path=source_path,
                map_path=map_path,
                file_description=make_placeholder("Describe this module"),
                file_description_is_placeholder=True,
                sections=sections,
            ),
            [],
            list(current_names),
        )

    # Merge with existing
    existing_names = set(existing.sections.keys())

    removed = list(existing_names - current_names)
    added = list(current_names - existing_names)

    sections = []
    for s in symbols:
        if s.name in existing.sections:
            # Preserve existing content
            old = existing.sections[s.name]
            sections.append(
                Section(
                    symbol_name=s.name,
                    symbol_kind=s.kind,
                    line_number=s.line,  # Updated line number
                    description=old.description,  # Preserved
                    is_placeholder=old.is_placeholder,
                )
            )
        else:
            # New symbol
            sections.append(
                Section(
                    symbol_name=s.name,
                    symbol_kind=s.kind,
                    line_number=s.line,
                    description=make_placeholder(f"Describe {s.name}"),
                    is_placeholder=True,
                )
            )

    # Preserve file description if filled
    file_desc = existing.file_description
    file_desc_is_placeholder = existing.file_description_is_placeholder
    if file_desc_is_placeholder:
        file_desc = make_placeholder("Describe this module")

    return (
        MapFile(
            source_path=source_path,
            map_path=map_path,
            file_description=file_desc,
            file_description_is_placeholder=file_desc_is_placeholder,
            sections=sections,
        ),
        removed,
        added,
    )
