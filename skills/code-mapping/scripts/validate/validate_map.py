"""Map validator module.

Validates code maps for structural integrity, link validity, and size limits.
"""

import re
from dataclasses import dataclass
from pathlib import Path

try:
    from .lsp_client import symbol_at_line, symbol_exists
except ImportError:
    from lsp_client import symbol_at_line, symbol_exists


@dataclass
class ValidationError:
    """Represents a validation error."""

    file: str
    line: int
    message: str
    error_type: str  # "structure", "broken_link", "broken_symbol", "size_limit"


# Size limits by level
SIZE_LIMITS = {
    "L0": 500,  # ARCHITECTURE.md
    "L1": 300,  # domains/*.md
    "L2": 200,  # modules/**/*.md
}


def validate_map(map_dir: Path) -> list[ValidationError]:
    """Main entry point for map validation.

    Args:
        map_dir: Path to the map directory (e.g., docs/map).

    Returns:
        List of validation errors found.
    """
    errors = []
    errors.extend(check_structure(map_dir))
    errors.extend(check_file_links(map_dir))
    errors.extend(check_code_links(map_dir))
    errors.extend(check_size_limits(map_dir))
    return errors


def check_structure(map_dir: Path) -> list[ValidationError]:
    """Verify required files exist.

    Args:
        map_dir: Path to the map directory.

    Returns:
        List of structural validation errors.
    """
    errors = []

    readme = map_dir / "README.md"
    if not readme.exists():
        errors.append(
            ValidationError(
                file=str(readme),
                line=0,
                message="README.md not found",
                error_type="structure",
            )
        )

    arch_md = map_dir / "ARCHITECTURE.md"
    if not arch_md.exists():
        errors.append(
            ValidationError(
                file=str(arch_md),
                line=0,
                message="ARCHITECTURE.md not found",
                error_type="structure",
            )
        )

    domains_dir = map_dir / "domains"
    if not domains_dir.exists():
        errors.append(
            ValidationError(
                file=str(domains_dir),
                line=0,
                message="domains/ directory not found",
                error_type="structure",
            )
        )

    return errors


# Regex patterns for markdown links
# Standard link: [text](path.md) or [text](path.md#anchor)
FILE_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)#]+)(?:#[^)]+)?\)")
# Code link: [`symbol`](path.py#L42)
CODE_LINK_PATTERN = re.compile(r"\[`([^`]+)`\]\(([^)#]+)#L(\d+)\)")
# Source link: [Source](path.py#L42) - links to a file line without symbol name
SOURCE_LINK_PATTERN = re.compile(r"\[Source\]\(([^)#]+)#L(\d+)\)")


def _is_in_code_context(line: str, match_start: int) -> bool:
    """Check if a match position is within inline code backticks.

    Handles both single backtick and double backtick inline code.

    Args:
        line: The line of text.
        match_start: Starting position of the match in the line.

    Returns:
        True if the match is inside backticks.
    """
    prefix = line[:match_start]

    # Handle double backtick (`` code ``) - count pairs
    double_backtick_count = prefix.count("``")
    if double_backtick_count % 2 == 1:
        return True

    # Handle single backtick - count singles (excluding doubles)
    # Remove double backticks first to count only single ones
    single_only = prefix.replace("``", "")
    if single_only.count("`") % 2 == 1:
        return True

    return False


def check_file_links(map_dir: Path) -> list[ValidationError]:
    """Validate all file links in map documents.

    Args:
        map_dir: Path to the map directory.

    Returns:
        List of broken link errors.
    """
    errors = []

    for md_file in map_dir.rglob("*.md"):
        content = md_file.read_text()
        lines = content.split("\n")
        in_code_block = False

        for line_num, line in enumerate(lines, start=1):
            # Track fenced code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip lines in fenced code blocks
            if in_code_block:
                continue

            # Find all standard links
            for match in FILE_LINK_PATTERN.finditer(line):
                # Skip if within inline code backticks
                if _is_in_code_context(line, match.start()):
                    continue

                link_text = match.group(1)
                link_path = match.group(2)

                # Skip external URLs
                if link_path.startswith(("http://", "https://", "mailto:")):
                    continue

                # Skip code links (handled separately)
                if link_text.startswith("`") and "#L" in match.group(0):
                    continue

                # Skip python file links (handled by code link checker)
                if link_path.endswith(".py"):
                    continue

                # Resolve relative path
                target = (md_file.parent / link_path).resolve()

                if not target.exists():
                    errors.append(
                        ValidationError(
                            file=str(md_file.relative_to(map_dir)),
                            line=line_num,
                            message=f"[{link_text}]({link_path}) -> file not found",
                            error_type="broken_link",
                        )
                    )

    return errors


def check_code_links(map_dir: Path) -> list[ValidationError]:
    """Validate all code links in map documents.

    Code links have format: [`symbol`](path/to/file.py#L42)
    Source links have format: [Source](path/to/file.py#L42)

    Args:
        map_dir: Path to the map directory.

    Returns:
        List of broken code link errors.
    """
    errors = []

    for md_file in map_dir.rglob("*.md"):
        content = md_file.read_text()
        lines = content.split("\n")
        in_code_block = False

        for line_num, line in enumerate(lines, start=1):
            # Track fenced code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip lines in fenced code blocks
            if in_code_block:
                continue

            # Check symbol code links: [`symbol`](path.py#L42)
            for match in CODE_LINK_PATTERN.finditer(line):
                # Skip if within inline code backticks
                if _is_in_code_context(line, match.start()):
                    continue

                symbol_name = match.group(1)
                file_path = match.group(2)
                line_number = int(match.group(3))

                # Resolve relative path from the markdown file's location
                target = (md_file.parent / file_path).resolve()

                if not target.exists():
                    msg = (
                        f"[`{symbol_name}`]({file_path}#L{line_number}) "
                        f"-> file not found"
                    )
                    errors.append(
                        ValidationError(
                            file=str(md_file.relative_to(map_dir)),
                            line=line_num,
                            message=msg,
                            error_type="broken_symbol",
                        )
                    )
                    continue

                # Check if symbol exists anywhere in file
                if not symbol_exists(target, symbol_name):
                    msg = (
                        f"[`{symbol_name}`]({file_path}#L{line_number}) "
                        f"-> symbol not found"
                    )
                    errors.append(
                        ValidationError(
                            file=str(md_file.relative_to(map_dir)),
                            line=line_num,
                            message=msg,
                            error_type="broken_symbol",
                        )
                    )
                    continue

                # Check if symbol is at the right line (with tolerance)
                if not symbol_at_line(target, symbol_name, line_number, tolerance=5):
                    msg = (
                        f"[`{symbol_name}`]({file_path}#L{line_number}) "
                        f"-> symbol not at line {line_number}"
                    )
                    errors.append(
                        ValidationError(
                            file=str(md_file.relative_to(map_dir)),
                            line=line_num,
                            message=msg,
                            error_type="broken_symbol",
                        )
                    )

            # Check source links: [Source](path.py#L42)
            for match in SOURCE_LINK_PATTERN.finditer(line):
                if _is_in_code_context(line, match.start()):
                    continue

                file_path = match.group(1)
                line_number = int(match.group(2))

                target = (md_file.parent / file_path).resolve()

                if not target.exists():
                    msg = f"[Source]({file_path}#L{line_number}) -> file not found"
                    errors.append(
                        ValidationError(
                            file=str(md_file.relative_to(map_dir)),
                            line=line_num,
                            message=msg,
                            error_type="broken_symbol",
                        )
                    )
                    continue

                # Check line number is within file bounds
                try:
                    file_lines = target.read_text().split("\n")
                    if line_number > len(file_lines):
                        msg = (
                            f"[Source]({file_path}#L{line_number}) "
                            f"-> line {line_number} exceeds file length "
                            f"({len(file_lines)} lines)"
                        )
                        errors.append(
                            ValidationError(
                                file=str(md_file.relative_to(map_dir)),
                                line=line_num,
                                message=msg,
                                error_type="broken_symbol",
                            )
                        )
                except (OSError, UnicodeDecodeError):
                    pass  # File read error, already caught by file exists check

    return errors


def check_size_limits(map_dir: Path) -> list[ValidationError]:
    """Validate file size limits.

    Args:
        map_dir: Path to the map directory.

    Returns:
        List of size limit errors.
    """
    errors = []

    # Check L0 (ARCHITECTURE.md)
    arch_md = map_dir / "ARCHITECTURE.md"
    if arch_md.exists():
        line_count = len(arch_md.read_text().split("\n"))
        limit = SIZE_LIMITS["L0"]
        if line_count > limit:
            errors.append(
                ValidationError(
                    file="ARCHITECTURE.md",
                    line=0,
                    message=f"Exceeds L0 limit: {line_count} lines > {limit}",
                    error_type="size_limit",
                )
            )

    # Check L1 (domains/*.md)
    domains_dir = map_dir / "domains"
    if domains_dir.exists():
        limit = SIZE_LIMITS["L1"]
        for domain_file in domains_dir.glob("*.md"):
            line_count = len(domain_file.read_text().split("\n"))
            if line_count > limit:
                errors.append(
                    ValidationError(
                        file=f"domains/{domain_file.name}",
                        line=0,
                        message=f"Exceeds L1 limit: {line_count} lines > {limit}",
                        error_type="size_limit",
                    )
                )

    # Check L2 (modules/**/*.md)
    modules_dir = map_dir / "modules"
    if modules_dir.exists():
        limit = SIZE_LIMITS["L2"]
        for module_file in modules_dir.rglob("*.md"):
            line_count = len(module_file.read_text().split("\n"))
            if line_count > limit:
                relative_path = module_file.relative_to(map_dir)
                errors.append(
                    ValidationError(
                        file=str(relative_path),
                        line=0,
                        message=f"Exceeds L2 limit: {line_count} lines > {limit}",
                        error_type="size_limit",
                    )
                )

    return errors
