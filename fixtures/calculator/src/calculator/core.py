"""Core Calculator class."""

from .operations import add, divide, multiply, subtract


class Calculator:
    """A simple calculator with memory."""

    def __init__(self, initial_value: float = 0.0):
        """Initialize calculator with optional starting value."""
        self._value = initial_value
        self._history: list[str] = []

    @property
    def value(self) -> float:
        """Current value in memory."""
        return self._value

    @property
    def history(self) -> list[str]:
        """List of operations performed."""
        return self._history.copy()

    def add(self, x: float) -> "Calculator":
        """Add x to current value."""
        self._value = add(self._value, x)
        self._history.append(f"+ {x}")
        return self

    def subtract(self, x: float) -> "Calculator":
        """Subtract x from current value."""
        self._value = subtract(self._value, x)
        self._history.append(f"- {x}")
        return self

    def multiply(self, x: float) -> "Calculator":
        """Multiply current value by x."""
        self._value = multiply(self._value, x)
        self._history.append(f"* {x}")
        return self

    def divide(self, x: float) -> "Calculator":
        """Divide current value by x."""
        self._value = divide(self._value, x)
        self._history.append(f"/ {x}")
        return self

    def clear(self) -> "Calculator":
        """Reset calculator to zero."""
        self._value = 0.0
        self._history.clear()
        return self
