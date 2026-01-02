# [L2:calculator.core] core

Core Calculator class.

---

## Classes

### Calculator

A simple calculator with memory.

#### `__init__(self, initial_value: float = 0.0)`

Initialize calculator with optional starting value.

[Source](../../../../src/calculator/core.py#L9)

#### `value(self) -> float`

Current value in memory.

[Source](../../../../src/calculator/core.py#L15)

#### `history(self) -> list[str]`

List of operations performed.

[Source](../../../../src/calculator/core.py#L20)

#### `add(self, x: float) -> 'Calculator'`

Add x to current value.

[Source](../../../../src/calculator/core.py#L24)

#### `subtract(self, x: float) -> 'Calculator'`

Subtract x from current value.

[Source](../../../../src/calculator/core.py#L30)

#### `multiply(self, x: float) -> 'Calculator'`

Multiply current value by x.

[Source](../../../../src/calculator/core.py#L36)

#### `divide(self, x: float) -> 'Calculator'`

Divide current value by x.

[Source](../../../../src/calculator/core.py#L42)

#### `clear(self) -> 'Calculator'`

<!-- TODO: Add docstring to Calculator.clear -->

[Source](../../../../src/calculator/core.py#L48)
