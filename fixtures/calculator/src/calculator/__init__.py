"""Calculator package - a simple arithmetic library."""

from .core import Calculator
from .operations import add, divide, multiply, subtract

__all__ = ["Calculator", "add", "subtract", "multiply", "divide"]
