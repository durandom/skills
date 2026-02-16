"""Snapshot tests for map validator.

Tests run the CLI via subprocess and snapshot stdout.
"""

import subprocess
import sys
from pathlib import Path

# Path to code_map.py CLI
CODE_MAP_CLI = (
    Path(__file__).parent.parent.parent / "skills/code-mapping/scripts/code_map.py"
)


def run_code_map(*args: str, cwd: Path | None = None) -> tuple[str, str, int]:
    """Run code_map.py CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, str(CODE_MAP_CLI), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.stdout, result.stderr, result.returncode


# Get the path to our test fixtures
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
VALID_MAP = FIXTURES_DIR / "calculator" / "docs" / "map"


PROJECT_ROOT = Path(__file__).parent.parent.parent


def normalize_paths(output: str, tmp_path: Path | None = None) -> str:
    """Replace temp/project paths for deterministic snapshots.

    Also strips trailing whitespace from lines to match pre-commit hooks.
    """
    normalized = output
    if tmp_path:
        normalized = normalized.replace(str(tmp_path), "<TMP>")
    normalized = normalized.replace(str(PROJECT_ROOT), "<PROJECT>")
    # Strip trailing whitespace from each line (matching pre-commit behavior)
    lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(lines).rstrip() + "\n"


class TestValidMapSnapshot:
    """Snapshot tests for valid calculator map."""

    def test_valid_map_validation(self, snapshot):
        """Validate the calculator fixture map."""
        stdout, _stderr, code = run_code_map("validate", str(VALID_MAP))

        assert code == 0
        normalized = normalize_paths(stdout)
        assert normalized == snapshot


class TestBrokenMapSnapshots:
    """Snapshot tests for various broken map scenarios."""

    def test_missing_structure(self, snapshot, tmp_path):
        """Empty directory fails structure check."""
        stdout, _stderr, code = run_code_map("validate", str(tmp_path))

        assert code == 1  # Should fail
        normalized = normalize_paths(stdout, tmp_path)
        assert normalized == snapshot

    def test_broken_file_link(self, snapshot, tmp_path):
        """Map with broken file link."""
        (tmp_path / "MAP.md").write_text("# Map\n\n[Missing Link](does-not-exist.md)\n")
        (tmp_path / "ARCHITECTURE.md").write_text("# Architecture\n")
        (tmp_path / "domains").mkdir()

        stdout, _stderr, code = run_code_map("validate", str(tmp_path))

        assert code == 1
        normalized = normalize_paths(stdout, tmp_path)
        assert normalized == snapshot

    def test_broken_code_link(self, snapshot, tmp_path):
        """Map with broken code symbol reference."""
        # Create a Python file
        (tmp_path / "code.py").write_text("def real_function():\n    pass\n")

        # Create map referencing non-existent symbol
        (tmp_path / "MAP.md").write_text("# Map\n")
        (tmp_path / "ARCHITECTURE.md").write_text(
            "# Arch\n\n[`fake_function`](code.py#L1)\n"
        )
        (tmp_path / "domains").mkdir()

        stdout, _stderr, code = run_code_map("validate", str(tmp_path))

        assert code == 1
        normalized = normalize_paths(stdout, tmp_path)
        assert normalized == snapshot

    def test_size_limit_exceeded(self, snapshot, tmp_path):
        """Map with files exceeding size limits."""
        (tmp_path / "MAP.md").write_text("# Map\n")
        # L0 limit is 500 lines - create 510 lines
        (tmp_path / "ARCHITECTURE.md").write_text("# Arch\n" + "line\n" * 510)
        (tmp_path / "domains").mkdir()
        # L1 limit is 300 lines - create 310 lines
        (tmp_path / "domains" / "big.md").write_text("# Big\n" + "line\n" * 310)

        stdout, _stderr, code = run_code_map("validate", str(tmp_path))

        assert code == 1
        normalized = normalize_paths(stdout, tmp_path)
        assert normalized == snapshot
