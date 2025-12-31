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
            code_link_count += len(re.findall(r"\[`[^`]+`\]\([^)]+#L\d+\)", content))
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

    # Print summary
    print(f"Created: {len(report.created_files)} files")
    print(f"Updated: {len(report.updated_files)} files")
    print(f"Orphaned: {len(report.deleted_files)} files")
    print(f"Unfilled: {len(report.unfilled_placeholders)} placeholders")
    print()

    if report.created_files:
        print("Created files:")
        for f in report.created_files:
            print(f"  {f}")
        print()

    if report.new_sections:
        print("New sections:")
        for path, symbol in sorted(report.new_sections):
            print(f"  {path}: {symbol}")
        print()

    if report.removed_sections:
        print("Removed sections (code deleted):")
        for path, symbol in sorted(report.removed_sections):
            print(f"  {path}: {symbol}")
        print()

    if report.deleted_files:
        print("Orphaned maps (source deleted):")
        for f in report.deleted_files:
            print(f"  {f}")
        print()

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
