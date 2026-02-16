"""Snapshot tests for code map generation.

Tests run the CLI via subprocess and snapshot stdout.
Generated files are compared against fixtures/calculator/docs/map/.
"""

import shutil
import subprocess
import sys
from pathlib import Path

# Path to code_map.py CLI
CODE_MAP_CLI = (
    Path(__file__).parent.parent.parent / "skills/code-mapping/scripts/code_map.py"
)

# Get the path to our test fixtures
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
CALCULATOR_SRC = FIXTURES_DIR / "calculator" / "src" / "calculator"
CALCULATOR_MAP = FIXTURES_DIR / "calculator" / "docs" / "map"


def run_code_map(*args: str, cwd: Path | None = None) -> tuple[str, str, int]:
    """Run code_map.py CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, str(CODE_MAP_CLI), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.stdout, result.stderr, result.returncode


PROJECT_ROOT = Path(__file__).parent.parent.parent


def normalize_paths(output: str, tmp_path: Path) -> str:
    """Replace temp paths with <TMP> for deterministic snapshots.

    Also replaces the project root path with <PROJECT> and strips
    trailing whitespace from lines to match pre-commit hooks.
    """
    normalized = output.replace(str(tmp_path), "<TMP>")
    normalized = normalized.replace(str(PROJECT_ROOT), "<PROJECT>")
    # Strip trailing whitespace from each line (matching pre-commit behavior)
    lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(lines).rstrip() + "\n"


def compare_to_fixture(generated_dir: Path, fixture_dir: Path) -> None:
    """Assert generated files match fixture directory (ignoring path differences)."""
    import re

    generated_files = {
        p.relative_to(generated_dir) for p in generated_dir.rglob("*.md")
    }
    fixture_files = {p.relative_to(fixture_dir) for p in fixture_dir.rglob("*.md")}

    if generated_files != fixture_files:
        missing = fixture_files - generated_files
        extra = generated_files - fixture_files
        msg = []
        if missing:
            msg.append(f"Missing files: {missing}")
        if extra:
            msg.append(f"Extra files: {extra}")
        raise AssertionError("\n".join(msg))

    for rel_path in generated_files:
        generated_content = (generated_dir / rel_path).read_text()
        fixture_content = (fixture_dir / rel_path).read_text()
        # Normalize paths (../../../src/calculator/ -> relative form)
        generated_content = re.sub(
            r"\.\./\.\./\.\./src/calculator/",
            "../../../src/calculator/",
            generated_content,
        )
        fixture_content = re.sub(
            r"\.\./\.\./\.\./src/calculator/",
            "../../../src/calculator/",
            fixture_content,
        )
        # Also normalize ../../src/calculator/ for ARCHITECTURE.md
        generated_content = re.sub(
            r"\.\./\.\./src/calculator/", "../../src/calculator/", generated_content
        )
        fixture_content = re.sub(
            r"\.\./\.\./src/calculator/", "../../src/calculator/", fixture_content
        )
        if generated_content != fixture_content:
            raise AssertionError(
                f"File {rel_path} differs from fixture:\n"
                f"Generated:\n{generated_content}\n\n"
                f"Fixture:\n{fixture_content}"
            )


class TestGenerateNewMap:
    """Snapshot tests for fresh map generation."""

    def test_generate_calculator_fixture(self, snapshot, tmp_path):
        """Generate maps from calculator fixture - compare to fixture."""
        # Create fixture-like structure: src/calculator/ and docs/map/
        src_dir = tmp_path / "src" / "calculator"
        map_dir = tmp_path / "docs" / "map"
        shutil.copytree(CALCULATOR_SRC, src_dir)

        stdout, stderr, code = run_code_map("generate", str(src_dir), str(map_dir))

        assert code == 0, f"CLI failed: {stderr}"

        # Snapshot the stdout
        normalized_stdout = normalize_paths(stdout, tmp_path)
        assert normalized_stdout == snapshot

        # Compare generated files to fixture
        compare_to_fixture(map_dir, CALCULATOR_MAP)


class TestGenerateIdempotent:
    """Snapshot tests for idempotent updates."""

    def test_second_run_no_changes(self, snapshot, tmp_path):
        """Running generate twice produces no new changes."""
        src_dir = tmp_path / "src" / "calculator"
        map_dir = tmp_path / "docs" / "map"
        shutil.copytree(CALCULATOR_SRC, src_dir)

        # First run
        run_code_map("generate", str(src_dir), str(map_dir))

        # Second run - this is what we snapshot
        stdout, _stderr, code = run_code_map("generate", str(src_dir), str(map_dir))

        assert code == 0
        normalized_stdout = normalize_paths(stdout, tmp_path)
        assert normalized_stdout == snapshot


class TestGenerateDetectsChanges:
    """Snapshot tests for change detection."""

    def test_detects_new_symbol(self, snapshot, tmp_path):
        """Adding a function is detected as new section."""
        src_dir = tmp_path / "src" / "calculator"
        map_dir = tmp_path / "docs" / "map"
        shutil.copytree(CALCULATOR_SRC, src_dir)

        # First run
        run_code_map("generate", str(src_dir), str(map_dir))

        # Add a new function
        ops_file = src_dir / "operations.py"
        ops_content = ops_file.read_text()
        ops_file.write_text(ops_content + "\n\ndef modulo(a, b):\n    return a % b\n")

        # Second run
        stdout, _stderr, code = run_code_map("generate", str(src_dir), str(map_dir))

        assert code == 0
        normalized_stdout = normalize_paths(stdout, tmp_path)
        assert normalized_stdout == snapshot

    def test_docstring_changes_update_map(self, snapshot, tmp_path):
        """Changing docstrings in source updates the map."""
        src_dir = tmp_path / "src" / "calculator"
        map_dir = tmp_path / "docs" / "map"
        shutil.copytree(CALCULATOR_SRC, src_dir)

        # First run
        run_code_map("generate", str(src_dir), str(map_dir))

        # Verify initial docstring is used (now in module files)
        module_file = map_dir / "modules" / "calculator" / "operations.md"
        content = module_file.read_text()
        assert "Add two numbers." in content  # Original docstring

        # Update the docstring in source
        ops_file = src_dir / "operations.py"
        ops_content = ops_file.read_text()
        ops_content = ops_content.replace(
            '"""Add two numbers."""',
            '"""Sum two numeric values together."""',
        )
        ops_file.write_text(ops_content)

        # Second run
        stdout, _stderr, code = run_code_map("generate", str(src_dir), str(map_dir))

        assert code == 0
        normalized_stdout = normalize_paths(stdout, tmp_path)
        assert normalized_stdout == snapshot

        # Verify the updated docstring is now in the map
        final_content = module_file.read_text()
        assert "Sum two numeric values together." in final_content

    def test_detects_removed_symbol(self, snapshot, tmp_path):
        """Removing a function is detected and reported."""
        src_dir = tmp_path / "src" / "calculator"
        map_dir = tmp_path / "docs" / "map"
        shutil.copytree(CALCULATOR_SRC, src_dir)

        # First run
        run_code_map("generate", str(src_dir), str(map_dir))

        # Remove the divide function completely
        ops_file = src_dir / "operations.py"
        ops_file.write_text('''"""Basic arithmetic operations."""


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b
''')

        # Second run
        stdout, _stderr, code = run_code_map("generate", str(src_dir), str(map_dir))

        assert code == 0
        normalized_stdout = normalize_paths(stdout, tmp_path)
        assert normalized_stdout == snapshot
