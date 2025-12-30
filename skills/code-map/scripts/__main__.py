#!/usr/bin/env python3
"""CLI entry point for code map validation.

Usage:
    python .claude/skills/code-map/scripts/__main__.py docs/map
    # or
    uv run python .claude/skills/code-map/scripts/__main__.py docs/map
"""

import sys
from pathlib import Path

# Add the scripts directory to path for relative imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from validate_map import (  # noqa: E402
    check_structure,
    check_file_links,
    check_code_links,
    check_size_limits,
)


def main():
    """Run map validation."""
    if len(sys.argv) < 2:
        print("Usage: python -m .claude.skills.code-map.scripts <map-dir>")
        print("Example: python -m .claude.skills.code-map.scripts docs/map")
        sys.exit(1)

    map_dir = Path(sys.argv[1])

    if not map_dir.exists():
        print(f"Error: {map_dir} does not exist")
        sys.exit(1)

    print(f"Validating {map_dir}...")
    print()

    # Run each check and report results
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
        # Count file links checked
        link_count = 0
        for md_file in map_dir.rglob("*.md"):
            content = md_file.read_text()
            import re

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
        # Count code links checked
        code_link_count = 0
        import re

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
        sys.exit(1)
    else:
        print("All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
