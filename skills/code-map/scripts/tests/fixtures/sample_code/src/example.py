"""Example Python module for testing symbol validation."""


def example_function():
    """A top-level function for testing."""
    return "example"


class ExampleClass:
    """A class for testing class symbol detection."""

    def __init__(self):
        """Initialize the class."""
        self.value = 42

    def example_method(self):
        """An instance method for testing method detection."""
        return self.value * 2


def another_function(x: int, y: int) -> int:
    """Another function with type hints."""
    return x + y
