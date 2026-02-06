# AI INSTRUCTION: PYTHON COMMENTING STANDARDS

> **ROLE:** You are an expert Python developer working in an Agentic workflow. **GOAL:** Write comments that act as _anchors_ and _prompts_ for future AI agents (and humans). **PRIME DIRECTIVE:** Your comments must explain _intent_ and _architecture_, not syntax.

## 1\. The Core Philosophy: "Comments are Prompts"

In this codebase, we do not write comments to explain Python syntax. We write comments to **guide the next AI agent** that touches this file.

- **OLD WAY:** Explaining _what_ the code is doing (e.g., `i += 1 # increment counter`).

- **NEW WAY:** Explaining _why_ the code exists and _what constraints_ must be preserved.

## 2\. The "Intent Anchor" Pattern

When writing logic that looks unusual, complex, or specific to a business rule, you must leave an "Anchor." This prevents future agents from "refactoring" necessary complexity away.

**Format:** `# [KEYWORD]: [Constraint/Reason]`

**Keywords:**

- `CRITICAL`: Code that looks wrong but is right (e.g., specific hacks for legacy systems).

- `INTENT`: The business goal of a block of code.

- `PERF`: Performance optimizations that sacrifice readability.

### Examples

❌ **Bad (Syntax-focused):**

```python
# Retry 3 times
for i in range(3):
    try:
        connect()
    except:
        time.sleep(1)
```

✅ **Good (Agent-focused):**

```python
# INTENT: We use a custom retry loop instead of the 'tenacity' library here
# because 'tenacity' introduces a slightly different thread-local state
# that causes conflicts with our specific version of Celery.
# CRITICAL: Do not refactor to use a decorator.
for i in range(3):
    # ... implementation ...
```

## 3\. Python Specifics: Docstrings vs. Block Comments

### A. Docstrings (`"""`) are for Interfaces

- **Use for:** Functions, Classes, Modules.

- **Content:** What goes in, what comes out, and exceptions raised.

- **Style:** Google or NumPy style.

### B. Block Comments (`#`) are for Implementation

- **Use for:** Inside the function body.

- **Content:** "Gotchas," architectural decisions, and step-by-step logic flows for complex algorithms.

**Example:**

```python
def calculate_tax(amount: int) -> int:
    """
    Calculates VAT for a given amount.

    Args:
        amount: In cents (to avoid floating point errors).

    Returns:
        Tax amount in cents.
    """
    # INTENT: We intentionally ignore the user's locale here because
    # all transactions in this specific module are mandated to be
    # processed under Irish tax law regardless of origin.
    tax_rate = 0.23

    return int(amount * tax_rate)
```

## 4\. The "File Header" Prompt

Every complex file must start with a module-level docstring that sets the "Context Window" for the AI.

**Template:**

```python
"""
@module: payment_gateway.py
@context: Handles the raw SOAP requests to the legacy banking API.
@architecture:
    - This module is an Adapter pattern.
    - It isolates the messy XML parsing from the rest of the clean domain logic.
@rules:
    - NEVER import 'requests'; strictly use 'httpx'.
    - All currency math must use Decimal, never float.
"""
```

## 5\. Type Hints as Documentation

Do not write comments that repeat type hints. Use `Annotated` if a type needs explanation.

❌ **Bad:**

```vbnet
# User ID is a string
user_id: str = get_id()
```

✅ **Good:**

```python
from typing import Annotated

# Using Annotated tells the AI *what kind* of string this is without a comment
UserId = Annotated[str, "UUID4 string, strict validation"]

user_id: UserId = get_id()
```

## 6\. Testing Comments

In test files, comments are **specifications**. They tell the AI what the test is _actually_ verifying, which helps when the AI needs to write the implementation later.

```python
def test_rate_limiter():
    # SCENARIO: A user spams the button 50 times in 1 second.
    # EXPECTATION: Only the first request succeeds; 49 return 429.
    # CRITICAL: The counter must reset exactly at the 1.0s mark, not rolling.
    pass
```

## 7\. Refactoring Checklist (For the AI)

Before you (the AI) refactor any code in this project, scan for comments starting with `CRITICAL` or `INTENT`.

- If you see `CRITICAL`, **assume the code is correct** even if it looks inefficient.

- If you see `INTENT`, ensure your new solution satisfies that specific business intent.
