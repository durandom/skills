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
    - MAP.md (index)
    - ARCHITECTURE.md (overview)
    - domains/{domain}.md (symbol documentation)

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

    # Generate MAP.md
    map_md_path = Path("MAP.md")
    map_md_content = _render_map_md(project_name, config.project_description, [domain])
    if not config.dry_run:
        map_dir.mkdir(parents=True, exist_ok=True)
        (map_dir / "MAP.md").write_text(map_md_content)
    if map_md_path not in existing_files:
        report.created_files.append(map_md_path)

    # Generate ARCHITECTURE.md
    arch_md_path = Path("ARCHITECTURE.md")
    arch_md_content = _render_architecture_md(
        project_name, config.project_description, [domain], src_dir, map_dir
    )
    if not config.dry_run:
        (map_dir / "ARCHITECTURE.md").write_text(arch_md_content)
    if arch_md_path not in existing_files:
        report.created_files.append(arch_md_path)

    # Generate domain file
    domains_dir = map_dir / "domains"
    domain_path = Path("domains") / f"{domain_id}.md"

    # Parse existing domain file for description preservation
    existing_domain = parse_existing_map(map_dir / domain_path)

    domain_content, sections = _render_domain_md(
        domain, src_dir, map_dir, existing_domain
    )
    if not config.dry_run:
        domains_dir.mkdir(parents=True, exist_ok=True)
        (map_dir / domain_path).write_text(domain_content)
    if domain_path not in existing_files:
        report.created_files.append(domain_path)

    # Create MapFile for tracking
    map_file = MapFile(
        source_path=Path(domain_id),  # Placeholder
        map_path=domain_path,
        file_description=domain.description,
        file_description_is_placeholder=is_placeholder(domain.description),
        sections=sections,
    )
    map_files.append(map_file)

    # Track unfilled placeholders
    if is_placeholder(config.project_description):
        report.unfilled_placeholders.append((Path("MAP.md"), "project"))
        report.unfilled_placeholders.append((Path("ARCHITECTURE.md"), "project"))

    if is_placeholder(domain.description):
        report.unfilled_placeholders.append((domain_path, "domain"))

    for section in sections:
        if section.is_placeholder:
            report.unfilled_placeholders.append((domain_path, section.symbol_name))

    # Track new sections (all symbols on first run)
    for module in modules:
        for sym in module.symbols:
            report.new_sections.append((domain_path, sym.name))

    return report, map_files


def _render_map_md(
    project_name: str, project_description: str, domains: list[Domain]
) -> str:
    """Render MAP.md from template."""
    domains_table = "\n".join(
        f"| {d.name} | [domains/{d.domain_id}.md](domains/{d.domain_id}.md) | "
        f"{d.description.replace('<!-- TODO: ', '').replace(' -->', '')} |"
        for d in domains
    )
    return render_template(
        "MAP.md",
        project_name=project_name,
        project_description=project_description,
        domains_table=domains_table,
    )


def _render_architecture_md(
    project_name: str,
    project_description: str,
    domains: list[Domain],
    src_dir: Path,
    map_dir: Path,
) -> str:
    """Render ARCHITECTURE.md from template."""
    # Domains table
    domains_table = "\n".join(
        f"| [{d.name}](domains/{d.domain_id}.md) | "
        f"{d.description.replace('<!-- TODO: ', '').replace(' -->', '')} |"
        for d in domains
    )

    # Entry points: first few public symbols from each module
    entry_points = []
    for domain in domains:
        for module in domain.modules:
            src_full = src_dir / module.source_path
            map_full = map_dir / "ARCHITECTURE.md"
            rel_src = compute_relative_path(map_full, src_full)
            for sym in module.symbols:
                if not sym.name.startswith("_") or sym.name == "__init__":
                    if sym.kind == SymbolKind.CLASS:
                        desc = f"<!-- TODO: Describe {sym.name} -->"
                    else:
                        desc = f"<!-- TODO: Describe {sym.name} -->"
                    entry_points.append(
                        f"| [`{sym.name}`]({rel_src}#L{sym.line}) | {desc} |"
                    )

    entry_points_table = "\n".join(entry_points[:10])  # Limit to 10 entry points

    return render_template(
        "ARCHITECTURE.md",
        project_name=project_name,
        project_description=project_description,
        domains_table=domains_table,
        entry_points_table=entry_points_table,
        data_flow="<!-- TODO: Describe data flow -->",
    )


def _render_domain_md(
    domain: Domain, src_dir: Path, map_dir: Path, existing=None
) -> tuple[str, list[Section]]:
    """Render a domain file from template.

    Args:
        domain: Domain to render.
        src_dir: Source directory.
        map_dir: Map directory.
        existing: Parsed existing map file for description preservation.

    Returns:
        Tuple of (rendered content, list of Section objects for tracking)
    """
    sections: list[Section] = []
    components_parts = []

    # Helper to get existing description or create placeholder
    def get_description(name: str) -> tuple[str, bool]:
        if existing and name in existing.sections:
            old = existing.sections[name]
            return old.description, old.is_placeholder
        return make_placeholder(f"Describe {name}"), True

    for module in domain.modules:
        src_full = src_dir / module.source_path
        map_full = map_dir / "domains" / f"{domain.domain_id}.md"
        rel_src = compute_relative_path(map_full, src_full)

        # Group symbols by type
        classes = [s for s in module.symbols if s.kind == SymbolKind.CLASS]
        functions = [s for s in module.symbols if s.kind == SymbolKind.FUNCTION]
        methods = [s for s in module.symbols if s.kind == SymbolKind.METHOD]

        module_name = module.source_path.stem.replace("_", " ").title()

        # Render functions as a table
        if functions:
            components_parts.append(f"### {module_name} Module")
            components_parts.append("")
            components_parts.append("| Function | Description |")
            components_parts.append("|----------|-------------|")
            for func in functions:
                desc, is_placeholder = get_description(func.name)
                components_parts.append(
                    f"| [`{func.name}`]({rel_src}#L{func.line}) | {desc} |"
                )
                sections.append(
                    Section(
                        symbol_name=func.name,
                        symbol_kind=SymbolKind.FUNCTION,
                        line_number=func.line,
                        description=desc,
                        is_placeholder=is_placeholder,
                    )
                )
            components_parts.append("")

        # Render classes with their methods
        if classes:
            for cls in classes:
                components_parts.append(f"### {cls.name} Class")
                components_parts.append("")
                desc, is_placeholder = get_description(cls.name)
                sections.append(
                    Section(
                        symbol_name=cls.name,
                        symbol_kind=SymbolKind.CLASS,
                        line_number=cls.line,
                        description=desc,
                        is_placeholder=is_placeholder,
                    )
                )

                # Find methods for this class
                class_methods = [m for m in methods if m.parent == cls.name]
                if class_methods:
                    components_parts.append("| Member | Description |")
                    components_parts.append("|--------|-------------|")
                    components_parts.append(
                        f"| [`{cls.name}`]({rel_src}#L{cls.line}) | {desc} |"
                    )
                    for method in class_methods:
                        m_desc, m_is_placeholder = get_description(method.name)
                        row = (
                            f"| [`{method.name}`]({rel_src}#L{method.line}) "
                            f"| {m_desc} |"
                        )
                        components_parts.append(row)
                        sections.append(
                            Section(
                                symbol_name=method.name,
                                symbol_kind=SymbolKind.METHOD,
                                line_number=method.line,
                                description=m_desc,
                                is_placeholder=m_is_placeholder,
                            )
                        )
                    components_parts.append("")

    components = "\n".join(components_parts)

    content = render_template(
        "domain.md",
        domain_id=domain.domain_id,
        domain_name=domain.name,
        domain_description=domain.description,
        components=components,
    )

    return content, sections
