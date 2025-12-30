"""Tests for LSP client module.

TDD approach: These tests are written first to define the expected behavior.
"""

from pathlib import Path

# Get the path to our test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CODE = FIXTURES_DIR / "sample_code" / "src" / "example.py"


class TestSymbolExists:
    """Test symbol_exists function."""

    def test_symbol_exists_for_function(self):
        """Pyright finds top-level function."""
        from ..lsp_client import symbol_exists

        result = symbol_exists(SAMPLE_CODE, "example_function")
        assert result is True

    def test_symbol_exists_for_class(self):
        """Pyright finds class definition."""
        from ..lsp_client import symbol_exists

        result = symbol_exists(SAMPLE_CODE, "ExampleClass")
        assert result is True

    def test_symbol_exists_for_method(self):
        """Pyright finds method within class."""
        from ..lsp_client import symbol_exists

        # Methods are searched within their class context
        result = symbol_exists(SAMPLE_CODE, "example_method")
        assert result is True

    def test_symbol_not_found(self):
        """Returns False for nonexistent symbol."""
        from ..lsp_client import symbol_exists

        result = symbol_exists(SAMPLE_CODE, "nonexistent_function")
        assert result is False

    def test_handles_missing_file(self):
        """Graceful handling of missing files."""
        from ..lsp_client import symbol_exists

        missing_file = Path("/nonexistent/path/file.py")
        result = symbol_exists(missing_file, "any_symbol")
        assert result is False


class TestGetSymbols:
    """Test get_symbols function."""

    def test_returns_list_of_symbols(self):
        """Returns a list of Symbol objects."""
        from ..lsp_client import get_symbols, Symbol

        symbols = get_symbols(SAMPLE_CODE)
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        assert all(isinstance(s, Symbol) for s in symbols)

    def test_finds_function_with_line_number(self):
        """Function symbol includes line number."""
        from ..lsp_client import get_symbols

        symbols = get_symbols(SAMPLE_CODE)
        func_symbols = [s for s in symbols if s.name == "example_function"]
        assert len(func_symbols) == 1
        assert func_symbols[0].line == 4  # Line where def starts

    def test_finds_class_with_line_number(self):
        """Class symbol includes line number."""
        from ..lsp_client import get_symbols

        symbols = get_symbols(SAMPLE_CODE)
        class_symbols = [s for s in symbols if s.name == "ExampleClass"]
        assert len(class_symbols) == 1
        assert class_symbols[0].line == 9  # Line where class starts

    def test_returns_empty_for_missing_file(self):
        """Returns empty list for missing files."""
        from ..lsp_client import get_symbols

        missing_file = Path("/nonexistent/path/file.py")
        symbols = get_symbols(missing_file)
        assert symbols == []


class TestSymbolAtLine:
    """Test symbol_at_line function."""

    def test_symbol_at_correct_line(self):
        """Returns True when symbol exists at specified line."""
        from ..lsp_client import symbol_at_line

        result = symbol_at_line(SAMPLE_CODE, "example_function", 4)
        assert result is True

    def test_symbol_at_wrong_line(self):
        """Returns False when symbol exists but at different line."""
        from ..lsp_client import symbol_at_line

        # example_function is at line 4, not 10
        result = symbol_at_line(SAMPLE_CODE, "example_function", 10)
        assert result is False

    def test_symbol_at_line_tolerance(self):
        """Allows small line number drift (e.g., +/- 2 lines)."""
        from ..lsp_client import symbol_at_line

        # example_function is at line 4, should accept line 5 or 6
        result = symbol_at_line(SAMPLE_CODE, "example_function", 5, tolerance=2)
        assert result is True

        result = symbol_at_line(SAMPLE_CODE, "example_function", 2, tolerance=2)
        assert result is True
