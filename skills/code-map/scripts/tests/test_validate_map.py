"""Tests for map validator module.

TDD approach: These tests are written first to define the expected behavior.
"""

from pathlib import Path

# Get the path to our test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_MAP = FIXTURES_DIR / "valid_map"
BROKEN_LINKS = FIXTURES_DIR / "broken_links"
BROKEN_SYMBOLS = FIXTURES_DIR / "broken_symbols"
SAMPLE_CODE = FIXTURES_DIR / "sample_code"


class TestCheckStructure:
    """Test structure validation."""

    def test_validates_structure(self):
        """Checks MAP.md, ARCHITECTURE.md, domains/ exist."""
        from ..validate_map import check_structure

        errors = check_structure(VALID_MAP)
        assert len(errors) == 0

    def test_missing_map_md(self):
        """Reports missing MAP.md."""
        from ..validate_map import check_structure

        errors = check_structure(BROKEN_SYMBOLS)  # Has domains/ but no MAP.md
        assert len(errors) > 0
        assert any("MAP.md" in e.message for e in errors)

    def test_missing_architecture_md(self):
        """Reports missing ARCHITECTURE.md."""
        from ..validate_map import check_structure

        errors = check_structure(BROKEN_LINKS)  # Has MAP.md but no ARCHITECTURE.md
        assert len(errors) > 0
        assert any("ARCHITECTURE.md" in e.message for e in errors)


class TestCheckFileLinks:
    """Test file link validation."""

    def test_finds_broken_file_links(self):
        """[Text](nonexistent.md) detected as error."""
        from ..validate_map import check_file_links

        errors = check_file_links(BROKEN_LINKS)
        assert len(errors) > 0
        # Should find the nonexistent.md link
        assert any("nonexistent" in e.message.lower() for e in errors)

    def test_validates_file_links(self):
        """[Text](existing.md) passes when file exists."""
        from ..validate_map import check_file_links

        errors = check_file_links(VALID_MAP)
        assert len(errors) == 0


class TestCheckCodeLinks:
    """Test code link validation."""

    def test_finds_broken_code_links(self):
        """[`symbol`](file.py#L99) - wrong line number detected."""
        from ..validate_map import check_code_links

        errors = check_code_links(BROKEN_SYMBOLS)
        assert len(errors) > 0
        # Should find missing_func or wrong line references
        assert any(
            "missing_func" in e.message or "symbol" in e.message.lower() for e in errors
        )

    def test_validates_code_links(self):
        """[`symbol`](file.py#L42) passes via LSP."""
        from ..validate_map import check_code_links

        errors = check_code_links(VALID_MAP)
        assert len(errors) == 0


class TestCheckSizeLimits:
    """Test size limit validation."""

    def test_checks_size_limits(self):
        """Files over limit flagged."""
        from ..validate_map import check_size_limits

        # Our test fixtures are all small, so should pass
        errors = check_size_limits(VALID_MAP)
        assert len(errors) == 0


class TestValidateMap:
    """Test full map validation."""

    def test_valid_map_passes(self):
        """Complete valid map returns no errors."""
        from ..validate_map import validate_map

        errors = validate_map(VALID_MAP)
        assert len(errors) == 0, f"Unexpected errors: {[e.message for e in errors]}"

    def test_invalid_map_returns_errors(self):
        """Invalid maps return error list."""
        from ..validate_map import validate_map

        errors = validate_map(BROKEN_LINKS)
        assert len(errors) > 0


class TestValidationError:
    """Test ValidationError dataclass."""

    def test_validation_error_fields(self):
        """ValidationError has expected fields."""
        from ..validate_map import ValidationError

        error = ValidationError(
            file="test.md", line=42, message="Something broke", error_type="broken_link"
        )
        assert error.file == "test.md"
        assert error.line == 42
        assert error.message == "Something broke"
        assert error.error_type == "broken_link"
