"""Main orchestrator for code map generation."""

from dataclasses import dataclass
from pathlib import Path

from .differ import parse_existing_map
from .models import ChangeReport, MapFile, MissingDocstring, Section, SymbolKind
from .parser import extract_symbols
from .renderer import compute_relative_path, is_placeholder, make_placeholder
from .templates import render_template


@dataclass
class GeneratorConfig:
    """Configuration for map generation."""

    src_dir: Path
    map_dir: Path
    project_name: str | None = None  # Auto-detected from src_dir if not set
    project_description: str = "<!-- TODO: Describe this project -->"
    src_glob: str = "**/*.py"
    dry_run: bool = False


@dataclass
class SourceModule:
    """Represents a source file and its extracted symbols."""

    source_path: Path  # Relative to src_dir
    symbols: list  # List of ExtractedSymbol


def generate_maps(config: GeneratorConfig) -> tuple[ChangeReport, list[MapFile]]:
    """Generate or update map files using template structure.

    Creates:
    - README.md (index)
    - ARCHITECTURE.md (overview)
    - domains/ (empty directory for agent to populate)
    - modules/{src_dir}/{module}.md (symbol documentation)

    Note: Domain files are NOT auto-generated. The agent should analyze
    the generated module docs and create semantic domain groupings.

    Args:
        config: Generation configuration.

    Returns:
        Tuple of (ChangeReport, list of MapFile objects).
    """
    report = ChangeReport()

    # Resolve paths to absolute for consistent path computation
    src_dir = config.src_dir.resolve()
    map_dir = config.map_dir.resolve()

    # Auto-detect project name from src_dir
    project_name = config.project_name or src_dir.name.replace("_", " ").title()

    # Find all Python files
    source_files = sorted(src_dir.glob(config.src_glob))
    source_files = [
        f
        for f in source_files
        if f.name != "__init__.py" and "__pycache__" not in str(f)
    ]

    # Extract symbols from all source files
    modules: list[SourceModule] = []
    for source_path in source_files:
        rel_src = source_path.relative_to(src_dir)
        symbols = extract_symbols(source_path)
        if symbols:
            modules.append(SourceModule(source_path=rel_src, symbols=symbols))

    # Use source directory as temporary grouping for module file paths
    # Domains are NOT auto-generated - agent should create them semantically
    domain_id = src_dir.name.lower()

    # Track created files
    map_files = []

    # Check what files exist for change detection
    existing_files = set()
    if map_dir.exists():
        existing_files = {p.relative_to(map_dir) for p in map_dir.rglob("*.md")}

    # Ensure map_dir exists
    if not config.dry_run:
        map_dir.mkdir(parents=True, exist_ok=True)

    # Generate README.md only if it doesn't exist (preserve manual edits)
    readme_path = Path("README.md")
    if readme_path not in existing_files:
        readme_content = _render_readme_md(project_name, config.project_description)
        if not config.dry_run:
            (map_dir / "README.md").write_text(readme_content)
        report.created_files.append(readme_path)

    # Generate ARCHITECTURE.md only if it doesn't exist (preserve manual edits)
    arch_md_path = Path("ARCHITECTURE.md")
    if arch_md_path not in existing_files:
        arch_md_content = _render_architecture_md(project_name)
        if not config.dry_run:
            (map_dir / "ARCHITECTURE.md").write_text(arch_md_content)
        report.created_files.append(arch_md_path)

    # Create empty domains directory for agent to populate
    if not config.dry_run:
        (map_dir / "domains").mkdir(parents=True, exist_ok=True)

    # Generate L2 module files first
    all_module_sections: list[Section] = []

    for module in modules:
        # Preserve directory structure: advanced/scientific.py -> advanced/scientific.md
        module_rel_path = module.source_path.with_suffix(".md")
        module_path = Path("modules") / domain_id / module_rel_path

        # Parse existing module file for description preservation
        existing_module = parse_existing_map(map_dir / module_path)

        module_content, sections = _render_module_md(
            module, domain_id, src_dir, map_dir, existing_module
        )

        if not config.dry_run:
            (map_dir / module_path).parent.mkdir(parents=True, exist_ok=True)
            (map_dir / module_path).write_text(module_content)

        if module_path not in existing_files:
            report.created_files.append(module_path)

        all_module_sections.extend(sections)

        # Create MapFile for tracking
        map_file = MapFile(
            source_path=module.source_path,
            map_path=module_path,
            file_description="",  # Module-level description
            file_description_is_placeholder=False,
            sections=sections,
        )
        map_files.append(map_file)

        # Track new sections
        for sym in module.symbols:
            report.new_sections.append((module_path, sym.name))

    # Track missing descriptions (high-level docs that need manual editing)
    # Domains are NOT auto-generated - agent creates them by analyzing modules
    if is_placeholder(config.project_description):
        report.missing_descriptions.append(Path("README.md"))
        report.missing_descriptions.append(Path("ARCHITECTURE.md"))

    # Track missing docstrings (source code that needs docstrings)
    for section in all_module_sections:
        if section.is_placeholder:
            # Find which module this section belongs to
            for module in modules:
                if any(s.name == section.symbol_name for s in module.symbols):
                    report.missing_docstrings.append(
                        MissingDocstring(
                            source_path=module.source_path,
                            line=section.line_number,
                            symbol_name=section.symbol_name,
                        )
                    )
                    break

    return report, map_files


def _render_readme_md(project_name: str, project_description: str) -> str:
    """Render README.md from template."""
    # Domains are created by agent, not auto-generated
    domains_table = "| *Create domains by analyzing modules* | | |"
    return render_template(
        "README.md",
        project_name=project_name,
        project_description=project_description,
        domains_table=domains_table,
    )


def _render_architecture_md(project_name: str) -> str:
    """Render ARCHITECTURE.md from template.

    Note: ARCHITECTURE.md is a placeholder scaffold. Entry points and data flow
    are intentionally left as TODOs for AI/human curation.
    """
    # Domains are created by agent, not auto-generated
    domains_table = "| *Analyze modules and create semantic domain groupings* | |"

    return render_template(
        "ARCHITECTURE.md",
        project_name=project_name,
        domains_table=domains_table,
    )


def _parse_docstring_sections(
    docstring: str | None,
) -> dict[str, list[tuple[str, str]]]:
    """Parse docstring to extract Args, Returns, and Raises sections.

    Args:
        docstring: The docstring to parse.

    Returns:
        Dict with 'args', 'returns', 'raises' keys containing
        lists of (name, description) tuples.
    """
    result: dict[str, list[tuple[str, str]]] = {
        "args": [],
        "returns": [],
        "raises": [],
    }

    if not docstring:
        return result

    import re

    lines = docstring.split("\n")
    current_section = None
    current_item = None
    current_desc_lines = []

    def flush_item():
        if current_item and current_section:
            desc = " ".join(current_desc_lines).strip()
            result[current_section].append((current_item, desc))

    for line in lines:
        stripped = line.strip()

        # Check for section headers
        if stripped in ("Args:", "Arguments:", "Parameters:"):
            flush_item()
            current_section = "args"
            current_item = None
            current_desc_lines = []
            continue
        elif stripped in ("Returns:", "Return:"):
            flush_item()
            current_section = "returns"
            current_item = None
            current_desc_lines = []
            continue
        elif stripped in ("Raises:", "Raise:"):
            flush_item()
            current_section = "raises"
            current_item = None
            current_desc_lines = []
            continue
        elif stripped.endswith(":") and not stripped.startswith(" "):
            # Another section we don't care about
            flush_item()
            current_section = None
            current_item = None
            current_desc_lines = []
            continue

        if current_section:
            # Parse item lines like "param_name: Description"
            item_match = re.match(r"^\s{4}(\w+)(?:\s*\([^)]+\))?:\s*(.*)$", line)
            if item_match:
                flush_item()
                current_item = item_match.group(1)
                current_desc_lines = (
                    [item_match.group(2)] if item_match.group(2) else []
                )
            elif current_item and line.startswith("        "):
                # Continuation line
                current_desc_lines.append(stripped)

    flush_item()
    return result


def _render_module_md(
    module: SourceModule,
    domain_id: str,
    src_dir: Path,
    map_dir: Path,
    existing=None,
) -> tuple[str, list[Section]]:
    """Render a module file (L2) with detailed symbol documentation.

    Args:
        module: Source module to render.
        domain_id: Parent domain identifier.
        src_dir: Source directory.
        map_dir: Map directory.
        existing: Parsed existing map file for description preservation.

    Returns:
        Tuple of (rendered content, list of Section objects for tracking)
    """
    from .parser import extract_module_docstring

    sections: list[Section] = []
    components_parts = []

    src_full = src_dir / module.source_path
    # Preserve directory structure: advanced/scientific.py -> advanced/scientific.md
    module_rel_path = module.source_path.with_suffix(".md")
    module_map_path = map_dir / "modules" / domain_id / module_rel_path
    rel_src = compute_relative_path(module_map_path, src_full)

    # Group symbols by type
    classes = [s for s in module.symbols if s.kind == SymbolKind.CLASS]
    functions = [s for s in module.symbols if s.kind == SymbolKind.FUNCTION]
    methods = [s for s in module.symbols if s.kind == SymbolKind.METHOD]

    module_name = module.source_path.stem
    # Build dotted module ID: advanced/scientific.py -> advanced.scientific
    module_id_parts = list(module.source_path.with_suffix("").parts)
    module_dotted = ".".join(module_id_parts)

    # Module docstring for description
    module_doc = extract_module_docstring(src_full)
    module_description = (
        module_doc.split("\n")[0].strip()
        if module_doc
        else make_placeholder(f"Add module docstring to {module_name}.py")
    )

    # Render classes
    if classes:
        components_parts.append("## Classes")
        components_parts.append("")

        for cls in classes:
            # Class heading
            components_parts.append(f"### {cls.name}")
            components_parts.append("")

            # Class docstring
            if cls.docstring:
                components_parts.append(cls.docstring.split("\n")[0])
            else:
                components_parts.append(
                    make_placeholder(f"Add docstring to class {cls.name}")  # noqa: E501
                )
            components_parts.append("")

            sections.append(
                Section(
                    symbol_name=cls.name,
                    symbol_kind=SymbolKind.CLASS,
                    line_number=cls.line,
                    description=cls.docstring.split("\n")[0] if cls.docstring else "",
                    is_placeholder=not cls.docstring,
                )
            )

            # Find methods for this class
            class_methods = [m for m in methods if m.parent == cls.name]
            for method in class_methods:
                sig = method.signature or "()"
                components_parts.append(f"#### `{method.name}{sig}`")
                components_parts.append("")

                # Method docstring (first line)
                if method.docstring:
                    first_line = method.docstring.split("\n")[0]
                    components_parts.append(first_line)
                else:
                    components_parts.append(
                        make_placeholder(f"Add docstring to {cls.name}.{method.name}")
                    )
                components_parts.append("")

                # Parse and render parameters
                parsed = _parse_docstring_sections(method.docstring)
                if parsed["args"]:
                    components_parts.append("**Parameters:**")
                    components_parts.append("")
                    components_parts.append("| Name | Description |")
                    components_parts.append("|------|-------------|")
                    for param_name, param_desc in parsed["args"]:
                        if param_name != "self":
                            components_parts.append(f"| {param_name} | {param_desc} |")
                    components_parts.append("")

                # Parse and render raises
                if parsed["raises"]:
                    components_parts.append("**Raises:**")
                    components_parts.append("")
                    components_parts.append("| Exception | Description |")
                    components_parts.append("|-----------|-------------|")
                    for exc_name, exc_desc in parsed["raises"]:
                        components_parts.append(f"| {exc_name} | {exc_desc} |")
                    components_parts.append("")

                # Source link
                components_parts.append(f"[Source]({rel_src}#L{method.line})")
                components_parts.append("")

                sections.append(
                    Section(
                        symbol_name=method.name,
                        symbol_kind=SymbolKind.METHOD,
                        line_number=method.line,
                        description=method.docstring.split("\n")[0]
                        if method.docstring
                        else "",
                        is_placeholder=not method.docstring,
                    )
                )

    # Render functions
    if functions:
        components_parts.append("## Functions")
        components_parts.append("")

        for func in functions:
            sig = func.signature or "()"
            components_parts.append(f"### `{func.name}{sig}`")
            components_parts.append("")

            # Function docstring (first line)
            if func.docstring:
                first_line = func.docstring.split("\n")[0]
                components_parts.append(first_line)
            else:
                components_parts.append(
                    make_placeholder(f"Add docstring to {func.name}")
                )
            components_parts.append("")

            # Parse and render parameters
            parsed = _parse_docstring_sections(func.docstring)
            if parsed["args"]:
                components_parts.append("**Parameters:**")
                components_parts.append("")
                components_parts.append("| Name | Description |")
                components_parts.append("|------|-------------|")
                for param_name, param_desc in parsed["args"]:
                    components_parts.append(f"| {param_name} | {param_desc} |")
                components_parts.append("")

            # Parse and render raises
            if parsed["raises"]:
                components_parts.append("**Raises:**")
                components_parts.append("")
                components_parts.append("| Exception | Description |")
                components_parts.append("|-----------|-------------|")
                for exc_name, exc_desc in parsed["raises"]:
                    components_parts.append(f"| {exc_name} | {exc_desc} |")
                components_parts.append("")

            # Source link
            components_parts.append(f"[Source]({rel_src}#L{func.line})")
            components_parts.append("")

            sections.append(
                Section(
                    symbol_name=func.name,
                    symbol_kind=SymbolKind.FUNCTION,
                    line_number=func.line,
                    description=func.docstring.split("\n")[0] if func.docstring else "",
                    is_placeholder=not func.docstring,
                )
            )

    components = "\n".join(components_parts)

    content = render_template(
        "module.md",
        module_id=f"{domain_id}.{module_dotted}",
        module_name=module_name,
        module_description=module_description,
        components=components,
    )

    return content, sections
