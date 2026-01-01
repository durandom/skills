"""Main orchestrator for code map generation."""

from dataclasses import dataclass, field
from pathlib import Path

from .differ import parse_existing_map
from .models import ChangeReport, MapFile, Section, SymbolKind
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


@dataclass
class Domain:
    """A domain grouping multiple source modules."""

    name: str
    domain_id: str
    description: str
    modules: list[SourceModule] = field(default_factory=list)


def generate_maps(config: GeneratorConfig) -> tuple[ChangeReport, list[MapFile]]:
    """Generate or update map files using template structure.

    Creates:
    - README.md (index)
    - ARCHITECTURE.md (overview)
    - domains/{domain}.md (domain documentation with module links)
    - modules/{domain}/{module}.md (symbol documentation)

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

    # Create a single domain from all modules
    domain_id = src_dir.name.lower()
    domain = Domain(
        name=project_name,
        domain_id=domain_id,
        description="<!-- TODO: Describe this domain -->",
        modules=modules,
    )

    # Track created files
    map_files = []

    # Check what files exist for change detection
    existing_files = set()
    if map_dir.exists():
        existing_files = {p.relative_to(map_dir) for p in map_dir.rglob("*.md")}

    # Generate README.md
    readme_path = Path("README.md")
    readme_content = _render_readme_md(
        project_name, config.project_description, [domain]
    )
    if not config.dry_run:
        map_dir.mkdir(parents=True, exist_ok=True)
        (map_dir / "README.md").write_text(readme_content)
    if readme_path not in existing_files:
        report.created_files.append(readme_path)

    # Generate ARCHITECTURE.md
    arch_md_path = Path("ARCHITECTURE.md")
    arch_md_content = _render_architecture_md(project_name, [domain])
    if not config.dry_run:
        (map_dir / "ARCHITECTURE.md").write_text(arch_md_content)
    if arch_md_path not in existing_files:
        report.created_files.append(arch_md_path)

    # Generate L2 module files first
    modules_dir = map_dir / "modules" / domain_id
    all_module_sections: list[Section] = []

    for module in modules:
        module_name = module.source_path.stem
        module_path = Path("modules") / domain_id / f"{module_name}.md"

        # Parse existing module file for description preservation
        existing_module = parse_existing_map(map_dir / module_path)

        module_content, sections = _render_module_md(
            module, domain_id, src_dir, map_dir, existing_module
        )

        if not config.dry_run:
            modules_dir.mkdir(parents=True, exist_ok=True)
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

    # Generate L1 domain file (with links to modules)
    domains_dir = map_dir / "domains"
    domain_path = Path("domains") / f"{domain_id}.md"

    # Parse existing domain file for description preservation
    existing_domain = parse_existing_map(map_dir / domain_path)

    domain_content = _render_domain_md(domain, existing_domain)
    if not config.dry_run:
        domains_dir.mkdir(parents=True, exist_ok=True)
        (map_dir / domain_path).write_text(domain_content)
    if domain_path not in existing_files:
        report.created_files.append(domain_path)

    # Track unfilled placeholders
    if is_placeholder(config.project_description):
        report.unfilled_placeholders.append((Path("README.md"), "project"))
        report.unfilled_placeholders.append((Path("ARCHITECTURE.md"), "project"))

    if is_placeholder(domain.description):
        report.unfilled_placeholders.append((domain_path, "domain"))

    for section in all_module_sections:
        if section.is_placeholder:
            # Find which module this section belongs to
            for module in modules:
                if any(s.name == section.symbol_name for s in module.symbols):
                    module_path = (
                        Path("modules") / domain_id / f"{module.source_path.stem}.md"
                    )
                    report.unfilled_placeholders.append(
                        (module_path, section.symbol_name)
                    )
                    break

    return report, map_files


def _render_readme_md(
    project_name: str, project_description: str, domains: list[Domain]
) -> str:
    """Render README.md from template."""
    domains_table = "\n".join(
        f"| {d.name} | [domains/{d.domain_id}.md](domains/{d.domain_id}.md) | "
        f"{d.description.replace('<!-- TODO: ', '').replace(' -->', '')} |"
        for d in domains
    )
    return render_template(
        "README.md",
        project_name=project_name,
        project_description=project_description,
        domains_table=domains_table,
    )


def _render_architecture_md(
    project_name: str,
    domains: list[Domain],
) -> str:
    """Render ARCHITECTURE.md from template.

    Note: ARCHITECTURE.md is a placeholder scaffold. Entry points and data flow
    are intentionally left as TODOs for AI/human curation.
    """
    # Domains table with links
    domains_table = "\n".join(
        f"| [{d.name}](domains/{d.domain_id}.md) | "
        f"{d.description.replace('<!-- TODO: ', '').replace(' -->', '')} |"
        for d in domains
    )

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
    module_map_path = map_dir / "modules" / domain_id / f"{module.source_path.stem}.md"
    rel_src = compute_relative_path(module_map_path, src_full)

    # Group symbols by type
    classes = [s for s in module.symbols if s.kind == SymbolKind.CLASS]
    functions = [s for s in module.symbols if s.kind == SymbolKind.FUNCTION]
    methods = [s for s in module.symbols if s.kind == SymbolKind.METHOD]

    module_name = module.source_path.stem

    # Module docstring for description
    module_doc = extract_module_docstring(src_full)
    module_description = (
        module_doc.split("\n")[0].strip()
        if module_doc
        else make_placeholder(f"Describe {module_name}")
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
                components_parts.append(make_placeholder(f"Describe {cls.name}"))
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
                    components_parts.append(make_placeholder(f"Describe {method.name}"))
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
                components_parts.append(make_placeholder(f"Describe {func.name}"))
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
        module_id=f"{domain_id}.{module_name}",
        module_name=module_name,
        module_description=module_description,
        components=components,
    )

    return content, sections


def _render_domain_md(domain: Domain, existing=None) -> str:
    """Render a domain file (L1) with links to module docs.

    Args:
        domain: Domain to render.
        existing: Parsed existing map file for description preservation.

    Returns:
        Rendered content string.
    """

    # Build modules table
    modules_rows = []
    for module in domain.modules:
        module_name = module.source_path.stem
        module_link = f"[{module_name}](../modules/{domain.domain_id}/{module_name}.md)"

        # Get module description from docstring
        # Note: We'd need the full path here, but we can use a placeholder
        # The actual description comes from the module docstring
        desc = make_placeholder(f"Describe {module_name}")

        # Try to get first line of module docstring
        if module.symbols:
            # Use class/function count as a simple summary
            classes = sum(1 for s in module.symbols if s.kind == SymbolKind.CLASS)
            functions = sum(1 for s in module.symbols if s.kind == SymbolKind.FUNCTION)
            parts = []
            if classes:
                parts.append(f"{classes} class{'es' if classes > 1 else ''}")
            if functions:
                parts.append(f"{functions} function{'s' if functions > 1 else ''}")
            if parts:
                desc = ", ".join(parts)

        modules_rows.append(f"| {module_link} | {desc} |")

    modules_table = "\n".join(modules_rows) if modules_rows else "| *No modules* | |"

    # Dependencies placeholder
    dependencies = make_placeholder("List cross-domain dependencies")

    return render_template(
        "domain.md",
        domain_id=domain.domain_id,
        domain_name=domain.name,
        domain_description=domain.description,
        modules_table=modules_table,
        dependencies=dependencies,
    )
