"""Markdown generation from MapFile structures."""

from pathlib import Path

from .models import MapFile, Section, SymbolKind

PLACEHOLDER_PREFIX = "<!-- TODO: "
PLACEHOLDER_SUFFIX = " -->"


def make_placeholder(hint: str) -> str:
    """Generate a placeholder with hint text.

    Args:
        hint: Description of what should be filled in.

    Returns:
        HTML comment placeholder string.
    """
    return f"{PLACEHOLDER_PREFIX}{hint}{PLACEHOLDER_SUFFIX}"


def is_placeholder(text: str) -> bool:
    """Check if text is an unfilled placeholder.

    Args:
        text: Text to check.

    Returns:
        True if text is a placeholder, False if filled.
    """
    stripped = text.strip()
    return stripped.startswith(PLACEHOLDER_PREFIX) and stripped.endswith(
        PLACEHOLDER_SUFFIX
    )


def compute_relative_path(from_map: Path, to_src: Path) -> str:
    """Compute relative path from map file to source file.

    Args:
        from_map: Path to the map markdown file (can be relative or absolute).
        to_src: Path to the source file (can be relative or absolute).

    Returns:
        Relative path string with forward slashes.
    """
    # Resolve to absolute paths for consistent comparison
    from_abs = from_map.resolve()
    to_abs = to_src.resolve()

    try:
        rel = to_abs.relative_to(from_abs.parent)
        return str(rel).replace("\\", "/")
    except ValueError:
        # Not a subpath, compute relative path via common ancestor
        from_parts = from_abs.parent.parts
        to_parts = to_abs.parts

        # Find common prefix length
        common_len = 0
        for a, b in zip(from_parts, to_parts):
            if a == b:
                common_len += 1
            else:
                break

        # Build relative path: go up from 'from', then down to 'to'
        ups = len(from_parts) - common_len
        rel_parts = [".."] * ups + list(to_parts[common_len:])
        return "/".join(rel_parts)


def render_map_file(map_file: MapFile, src_base: Path, map_base: Path) -> str:
    """Render a MapFile to markdown string.

    Args:
        map_file: The MapFile to render.
        src_base: Base directory for source files.
        map_base: Base directory for map files.

    Returns:
        Markdown string for the map file.
    """
    lines = []

    # Title
    lines.append(f"# {map_file.source_path.name}")
    lines.append("")

    # File description
    lines.append(map_file.file_description)
    lines.append("")

    # Compute relative path from map to source
    src_full = src_base / map_file.source_path
    map_full = map_base / map_file.map_path
    rel_src = compute_relative_path(map_full, src_full)

    # Group sections by kind
    classes = [s for s in map_file.sections if s.symbol_kind == SymbolKind.CLASS]
    functions = [s for s in map_file.sections if s.symbol_kind == SymbolKind.FUNCTION]
    methods_by_class: dict[str, list[Section]] = {}

    for s in map_file.sections:
        if s.symbol_kind == SymbolKind.METHOD:
            # Find parent class from symbol name pattern or section list
            for cls in classes:
                # Methods follow their parent class in the list
                methods_by_class.setdefault(cls.symbol_name, []).append(s)
                break

    # Actually, we need to track parent properly. Let me rebuild this logic.
    # Methods are associated with classes based on the order they appear.

    # Render classes with their methods
    if classes:
        lines.append("## Classes")
        lines.append("")

        for cls in classes:
            lines.append(f"### [`{cls.symbol_name}`]({rel_src}#L{cls.line_number})")
            lines.append("")
            lines.append(cls.description)
            lines.append("")

            # Find methods for this class
            class_methods = [
                s
                for s in map_file.sections
                if s.symbol_kind == SymbolKind.METHOD
                and _is_method_of_class(s, cls, map_file.sections)
            ]

            if class_methods:
                lines.append("**Methods:**")
                lines.append("")
                for method in class_methods:
                    line = (
                        f"- [`{method.symbol_name}`]({rel_src}#L{method.line_number}): "
                        f"{method.description}"
                    )
                    lines.append(line)
                lines.append("")

    # Render standalone functions
    if functions:
        lines.append("## Functions")
        lines.append("")

        for func in functions:
            lines.append(f"### [`{func.symbol_name}`]({rel_src}#L{func.line_number})")
            lines.append("")
            lines.append(func.description)
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _is_method_of_class(
    method: Section, cls: Section, all_sections: list[Section]
) -> bool:
    """Determine if a method belongs to a class based on line ordering.

    Methods appear after their class and before the next class in the list.
    """
    cls_idx = all_sections.index(cls)
    method_idx = all_sections.index(method)

    if method_idx <= cls_idx:
        return False

    # Check if there's another class between cls and method
    for i in range(cls_idx + 1, method_idx):
        if all_sections[i].symbol_kind == SymbolKind.CLASS:
            return False

    return True
