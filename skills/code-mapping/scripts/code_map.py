#!/usr/bin/env python3
"""CLI for code map tools.

Usage:
    python code_map.py validate <map-dir>
    python code_map.py generate <src-dir> <map-dir>
"""

import sys
from pathlib import Path

# Add the scripts directory to path for relative imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))


def cmd_validate(args: list[str]) -> int:
    """Run map validation."""
    if len(args) < 1:
        print("Usage: code_map.py validate <map-dir>")
        return 1

    from validate import (
        check_code_links,
        check_file_links,
        check_size_limits,
        check_structure,
    )

    map_dir = Path(args[0])

    if not map_dir.exists():
        print(f"Error: {map_dir} does not exist")
        return 1

    print(f"Validating {map_dir}...")
    print()

    all_errors = []

    # Structure check
    structure_errors = check_structure(map_dir)
    if structure_errors:
        print("Structure: FAIL")
        for err in structure_errors:
            print(f"  {err.file}: {err.message}")
        all_errors.extend(structure_errors)
    else:
        print("Structure: OK")

    # File links check
    file_link_errors = check_file_links(map_dir)
    if file_link_errors:
        print("File links: FAIL")
        for err in file_link_errors:
            print(f"  {err.file}:{err.line} - {err.message}")
        all_errors.extend(file_link_errors)
    else:
        import re

        link_count = 0
        for md_file in map_dir.rglob("*.md"):
            content = md_file.read_text()
            link_count += len(re.findall(r"\[[^\]]+\]\([^)]+\)", content))
        print(f"File links: OK ({link_count} checked)")

    # Code links check
    code_link_errors = check_code_links(map_dir)
    if code_link_errors:
        print("Code links: FAIL")
        for err in code_link_errors:
            print(f"  {err.file}:{err.line} - {err.message}")
        all_errors.extend(code_link_errors)
    else:
        import re

        code_link_count = 0
        for md_file in map_dir.rglob("*.md"):
            content = md_file.read_text()
            # Count symbol links [`sym`](path#L42) and [Source](path#L42)
            code_link_count += len(re.findall(r"\[`[^`]+`\]\([^)]+#L\d+\)", content))
            code_link_count += len(re.findall(r"\[Source\]\([^)]+#L\d+\)", content))
        print(f"Code links: OK ({code_link_count} checked, AST)")

    # Size limits check
    size_errors = check_size_limits(map_dir)
    if size_errors:
        print("Size limits: FAIL")
        for err in size_errors:
            print(f"  {err.file}: {err.message}")
        all_errors.extend(size_errors)
    else:
        print("Size limits: OK")

    print()

    if all_errors:
        print(f"{len(all_errors)} errors found.")
        return 1
    else:
        print("All checks passed.")
        return 0


def cmd_generate(args: list[str]) -> int:
    """Generate or update map files from source."""
    if len(args) < 2:
        print("Usage: code_map.py generate <src-dir> <map-dir>")
        return 1

    from generate import GeneratorConfig, generate_maps

    src_dir = Path(args[0])
    map_dir = Path(args[1])
    dry_run = "--dry-run" in args

    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist")
        return 1

    print(f"Generating maps: {src_dir} -> {map_dir}")
    if dry_run:
        print("(dry run)")
    print()

    config = GeneratorConfig(src_dir=src_dir, map_dir=map_dir, dry_run=dry_run)
    report, _ = generate_maps(config)

    # Output limit to avoid token bloat in large codebases
    MAX_ITEMS = 10

    # Print summary counts
    print("Summary:")
    print(f"  Created: {len(report.created_files)} files")
    print(f"  Updated: {len(report.updated_files)} files")
    if report.deleted_files:
        print(f"  Orphaned: {len(report.deleted_files)} files (source deleted)")
    print()

    # Show missing docstrings (the main actionable item)
    if report.missing_docstrings:
        shown = report.missing_docstrings[:MAX_ITEMS]
        remaining = len(report.missing_docstrings) - len(shown)
        print(f"Missing docstrings ({len(report.missing_docstrings)} total):")
        print("  Add docstrings to source, then re-run generator.")
        print()
        for item in shown:
            print(f"  {src_dir / item.source_path}:{item.line} - {item.symbol_name}")
        if remaining > 0:
            print(f"  ... and {remaining} more")
        print()

    # Show missing high-level descriptions
    if report.missing_descriptions:
        print(f"Missing descriptions ({len(report.missing_descriptions)} total):")
        print("  Edit these files directly (they're not auto-generated).")
        print()
        for path in report.missing_descriptions[:MAX_ITEMS]:
            print(f"  {map_dir / path}")
        if len(report.missing_descriptions) > MAX_ITEMS:
            print(f"  ... and {len(report.missing_descriptions) - MAX_ITEMS} more")
        print()

    # Show orphaned files that need cleanup
    if report.deleted_files:
        shown = report.deleted_files[:MAX_ITEMS]
        remaining = len(report.deleted_files) - len(shown)
        print("Orphaned map files (source was deleted):")
        for f in shown:
            print(f"  {f}")
        if remaining > 0:
            print(f"  ... and {remaining} more")
        print()

    # Skill path for referencing docs
    skill_path = Path(__file__).parent.parent

    # Next steps guidance (bottom-up: docstrings -> domains -> architecture)
    print("Next steps:")
    step = 1
    if report.missing_docstrings:
        print(f"  {step}. Add docstrings to source files listed above")
        step += 1
        print(f"  {step}. Re-run generator to update map")
        step += 1
    # Domains are never auto-generated - agent must create them
    print(f"  {step}. Create domain files by analyzing module docs")
    print("       Cluster modules into semantic groupings (not 1:1 with directories)")
    print(f"       See: {skill_path}/references/domains.md")
    step += 1
    if report.missing_descriptions:
        has_arch = any(
            "ARCHITECTURE" in str(p) or "README" in str(p)
            for p in report.missing_descriptions
        )
        if has_arch:
            print(f"  {step}. Write ARCHITECTURE.md (synthesize from domains)")
            step += 1
    if not report.missing_docstrings and not report.missing_descriptions:
        print(f"  {step}. Run validation: python code_map.py validate ...")
    print()
    print(f"See: {skill_path}/workflows/create.md for detailed guidance")

    return 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: code_map.py <command> [args]")
        print()
        print("Commands:")
        print("  validate <map-dir>           Validate existing map")
        print("  generate <src-dir> <map-dir> Generate/update map files")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "validate":
        sys.exit(cmd_validate(args))
    elif command == "generate":
        sys.exit(cmd_generate(args))
    else:
        print(f"Unknown command: {command}")
        print("Use 'validate' or 'generate'")
        sys.exit(1)


if __name__ == "__main__":
    main()
