# Recipe: Python Project Architecture for CLI Tools

**Target Audience:** Python developers and AI coding agents building CLI applications
**Goal:** Establish consistent patterns for maintainable, testable Python projects with SOLID principles

---

## Tech Stack Quick Reference

| Category | Tool | Why |
|----------|------|-----|
| **Package Manager** | uv | Fast, reproducible, replaces pip/pip-tools/virtualenv |
| **Build System** | hatchling | Standards-compliant (PEP 517/621), simple config |
| **CLI Framework** | Typer + Rich | Type-safe, beautiful output, shell completion |
| **Configuration** | Pydantic + pydantic-settings | Validation, env vars, .env files |
| **Logging** | loguru *or* stdlib `logging` | See note below |
| **Linting** | ruff | Unified (replaces flake8, isort, black) |
| **Type Checking** | mypy | Static analysis, catch errors early |
| **Testing** | pytest + syrupy | Markers, fixtures, snapshot testing |
| **Hooks** | pre-commit | Automated quality gates |

**Logging note:** `loguru` is convenient but non-standard. For libraries or team projects, consider stdlib `logging` which integrates with everything. Use `loguru` for standalone CLI tools where you control the entire stack.

---

## Choosing a Layout

| Layout | When to Use |
|--------|-------------|
| **Single Script** | One file, external deps via uv |
| **Flat Package** | 2-6 modules, installable CLI |
| **src Layout** | Libraries, team projects, PyPI publishing |

---

### Single Script

**When:** Everything fits in one file, but you need external packages.

```
project/
├── script.py
├── pyproject.toml
└── README.md
```

```toml
[project]
name = "my-script"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["httpx", "rich"]
```

```bash
uv sync && uv run script.py
```

---

### Flat Package

**When:** Code no longer fits in one file. You want `uv run mycmd` to work.

#### When to Split: Decision Criteria

| Signal | Action |
|--------|--------|
| File > 300 lines | Split by responsibility |
| Two distinct concerns (CLI vs logic) | `cli.py` + `core.py` |
| Reusable utilities emerging | `utils.py` or `helpers.py` |
| Multiple entry points | Separate command modules |
| Want to import from other projects | Need a package |

**Rule of thumb:** If you're scrolling a lot or functions feel unrelated, split.

#### Common Organization Patterns

**Pattern A: Core + CLI** (most common)

```
mypackage/
├── __init__.py      # Exports public API
├── __main__.py      # Enables: python -m mypackage
├── core.py          # Business logic (no CLI deps)
└── cli.py           # Typer app, imports from core
```

```python
# __main__.py - enables "python -m mypackage"
from .cli import app
app()

# core.py - pure logic, easy to test
def process_data(path: Path) -> dict:
    """Business logic with no UI concerns."""
    return {"files": list(path.glob("*"))}

# cli.py - thin wrapper
import typer
from .core import process_data

app = typer.Typer()

@app.command()
def run(path: Path):
    result = process_data(path)
    print(result)
```

**Pattern B: Feature-based** (when you have distinct features)

```
mypackage/
├── __init__.py
├── cli.py           # Main CLI, imports feature modules
├── auth.py          # Authentication feature
├── export.py        # Export feature
└── config.py        # Shared configuration
```

```python
# cli.py
import typer
from . import auth, export

app = typer.Typer()
app.add_typer(auth.app, name="auth")
app.add_typer(export.app, name="export")
```

**Pattern C: Types + Logic + CLI** (when you have complex data models)

```
mypackage/
├── __init__.py
├── types.py         # Dataclasses, Pydantic models, enums
├── core.py          # Logic using types
└── cli.py           # CLI using core
```

#### Import Rules

```python
# __init__.py - define your public API
from .core import process_data
from .types import Config

__all__ = ["process_data", "Config"]

# cli.py - import from package
from . import core                    # Relative import (preferred)
from .types import Config             # Specific import
from mypackage.core import process    # Absolute (works after install)
```

**Dependency direction:** `cli.py` → `core.py` → `types.py` (never reverse)

#### Avoiding Circular Imports with TYPE_CHECKING

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only imported during static analysis, not at runtime
    from .heavy_module import ExpensiveClass
    from .types import ComplexType

def process(data: "ComplexType") -> None:  # Forward reference as string
    ...
```

**Use `TYPE_CHECKING` when:**

- You have circular import issues
- Importing is expensive and only needed for type hints
- You want faster module load times

#### Flat Package pyproject.toml

```toml
[project]
name = "mypackage"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["typer", "rich"]

[project.scripts]
mycmd = "mypackage.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

```bash
uv sync              # Install deps
uv run mycmd         # Run CLI
```

---

### src Layout (Full)

**When:** Libraries, larger CLI tools, team projects, publishing to PyPI.

```
project-name/
├── src/project_name/           # Source code (src layout)
│   ├── __init__.py             # Package init + main() entry point
│   ├── __main__.py             # Enables: python -m project_name
│   ├── py.typed                # Marker: package supports type checking
│   ├── settings.py             # Pydantic Settings (env vars)
│   ├── core/                   # Business logic (no CLI deps)
│   │   ├── __init__.py
│   │   ├── config.py           # Domain config (Pydantic BaseModel)
│   │   ├── types.py            # Enums, dataclasses, type aliases
│   │   └── storage.py          # Example: ABC + implementations
│   └── cli/                    # CLI layer (Typer + Rich)
│       ├── __init__.py
│       ├── app.py              # Main Typer app + callback
│       ├── commands/           # Command modules
│       │   ├── __init__.py
│       │   ├── download.py
│       │   └── credentials.py
│       ├── formatters.py       # Output formatters (ABC pattern)
│       ├── schemas.py          # Output schemas (Pydantic)
│       └── utils.py            # CLI utilities (error handlers)
├── tests/
│   ├── conftest.py             # Shared fixtures
│   ├── unit/                   # Fast, isolated tests
│   └── e2e/                    # CLI integration tests
├── pyproject.toml              # All project config (single source of truth)
├── .pre-commit-config.yaml     # Quality hooks
├── .python-version             # Pin Python version (pyenv)
└── uv.lock                     # Reproducible dependencies
```

**Why src layout?**

- Prevents accidental imports from project root during development
- Forces you to install the package (catches missing dependencies)
- Standard for publishable packages

**The `py.typed` marker:** An empty file that tells type checkers (mypy, pyright) this package has inline type annotations. Required for PEP 561 compliance. Create it with `touch src/project_name/py.typed`.

### Key Separation (src layout)

| Directory | Contents | Dependencies |
|-----------|----------|--------------|
| `core/` | Business logic, domain models | Pydantic, standard library |
| `cli/` | User interface, formatting | Typer, Rich (can import core) |

**Rule:** `core/` must not import from `cli/`. This enables:

- Testing core logic without CLI
- Reusing core in other interfaces (API, SDK)
- Clear dependency direction

---

## SOLID Principles in Python

### Single Responsibility Principle (SRP)

**Each class has one reason to change.**

```python
# BAD: One class does everything
class CredentialManager:
    def load_from_file(self): ...
    def load_from_keyring(self): ...
    def save_to_file(self): ...
    def save_to_keyring(self): ...
    def validate(self): ...
    def refresh(self): ...

# GOOD: Separate concerns
@dataclass
class StoredCredentials:
    """Data container only."""
    token_data: dict[str, Any]
    client_id: str | None = None
    client_secret: str | None = None
    email: str | None = None


class FileCredentialStorage:
    """File-based storage only."""
    def load(self) -> StoredCredentials | None: ...
    def save(self, credentials: StoredCredentials) -> bool: ...


class KeyringCredentialStorage:
    """Keyring-based storage only."""
    def load(self) -> StoredCredentials | None: ...
    def save(self, credentials: StoredCredentials) -> bool: ...
```

**Guideline:** If a class has "and" in its description, it probably does too much.

---

### Open/Closed Principle (OCP)

**Open for extension, closed for modification.**

Python offers two approaches: **ABC** (inheritance-based) and **Protocol** (structural/duck typing). Prefer Protocol for flexibility.

#### Option A: Protocol (Pythonic, preferred)

```python
from typing import Protocol

class CredentialStorage(Protocol):
    """Structural interface - any class with these methods works."""

    def load(self, account_email: str | None = None) -> StoredCredentials | None: ...
    def save(self, credentials: StoredCredentials) -> bool: ...
    def delete(self, account_email: str | None = None) -> bool: ...

# No inheritance needed - just implement the methods
class FileCredentialStorage:
    def load(self, account_email: str | None = None) -> StoredCredentials | None:
        ...  # Implementation

    def save(self, credentials: StoredCredentials) -> bool:
        ...  # Implementation

    def delete(self, account_email: str | None = None) -> bool:
        ...  # Implementation
```

**Protocol benefits:** No inheritance required, works with existing classes, better for duck typing.

#### Option B: ABC (when you need shared implementation)

```python
from abc import ABC, abstractmethod

class CredentialStorage(ABC):
    """Use ABC when you have shared methods or want runtime isinstance() checks."""

    @abstractmethod
    def load(self, account_email: str | None = None) -> StoredCredentials | None: ...

    @abstractmethod
    def save(self, credentials: StoredCredentials) -> bool: ...

    # Shared implementation (reason to use ABC over Protocol)
    def load_or_raise(self, account_email: str | None = None) -> StoredCredentials:
        creds = self.load(account_email)
        if creds is None:
            raise ValueError("No credentials found")
        return creds
```

#### When to use which

| Use Protocol when... | Use ABC when... |
|---------------------|-----------------|
| Duck typing is sufficient | You need `isinstance()` checks |
| Working with third-party classes | You have shared method implementations |
| You want structural subtyping | You want to enforce inheritance |

#### Simple dependency injection (prefer over factories)

```python
# Pythonic: Just pass the dependency
class Exporter:
    def __init__(self, storage: CredentialStorage):
        self.storage = storage

# Usage
exporter = Exporter(storage=FileCredentialStorage(path))
```

---

### Liskov Substitution Principle (LSP)

**Subtypes must be substitutable for their base types.** Honor contracts.

```python
# Both implementations honor the same interface contract
class FileCredentialStorage(CredentialStorage):
    def load(self, account_email: str | None = None) -> StoredCredentials | None:
        # Returns StoredCredentials | None (contract fulfilled)
        if not self.token_path.exists():
            return None
        with open(self.token_path) as f:
            return StoredCredentials(token_data=json.load(f))

    def is_available(self) -> bool:
        return True  # File storage always available


class KeyringCredentialStorage(CredentialStorage):
    def load(self, account_email: str | None = None) -> StoredCredentials | None:
        # Returns StoredCredentials | None (contract fulfilled)
        data = self.keyring.get_password(self.service_name, account_email)
        if not data:
            return None
        return StoredCredentials(**json.loads(data))

    def is_available(self) -> bool:
        try:
            self.keyring.get_keyring()
            return True
        except Exception:
            return False
```

**Test:** Any code using `CredentialStorage` must work identically with either implementation.

---

### Interface Segregation Principle (ISP)

**Small, focused interfaces.** Don't force implementors to define methods they don't use.

```python
# GOOD: Focused interface (5 methods)
class CredentialStorage(ABC):
    @abstractmethod
    def load(self, account_email: str | None = None) -> StoredCredentials | None: ...
    @abstractmethod
    def save(self, credentials: StoredCredentials) -> bool: ...
    @abstractmethod
    def delete(self, account_email: str | None = None) -> bool: ...
    @abstractmethod
    def list_accounts(self) -> list[str]: ...
    @abstractmethod
    def is_available(self) -> bool: ...


# Additional methods on specific implementations (not in interface)
class KeyringCredentialStorage(CredentialStorage):
    # ... implements base interface ...

    # Keyring-specific methods (not forced on FileCredentialStorage)
    def save_client_credentials(self, creds: dict) -> bool: ...
    def load_client_credentials(self) -> dict | None: ...
```

**Guideline:** 5-6 abstract methods max. If more, consider splitting the interface.

---

### Dependency Inversion Principle (DIP)

**Depend on abstractions, not concretions.** Use factory functions and lazy loading.

```python
# BAD: Direct dependency on concrete class
class Exporter:
    def __init__(self):
        self.storage = FileCredentialStorage(Path("token.json"))  # Hardcoded!


# GOOD: Depend on abstraction via factory
class Exporter:
    def __init__(self, config: ExporterConfig):
        self.config = config

    def authenticate(self):
        # Factory function returns abstract CredentialStorage
        storage: CredentialStorage = get_credential_storage(
            use_keyring=self.config.use_keyring,
            token_path=self.config.token_path,
        )
        return storage.load()


# GOOD: Lazy loading for optional dependencies
class KeyringCredentialStorage(CredentialStorage):
    def __init__(self):
        self._keyring = None  # Deferred import

    @property
    def keyring(self):
        """Lazy import keyring module."""
        if self._keyring is None:
            import keyring  # Only imported when actually needed
            self._keyring = keyring
        return self._keyring
```

**Lazy loading benefits:**

- Faster startup (don't import unused modules)
- Graceful degradation (missing optional deps don't crash import)
- Cleaner test mocking

---

## Configuration Patterns

### Choosing Data Classes: dataclass vs Pydantic vs NamedTuple

| Type | When to Use | Validation | Mutability |
|------|-------------|------------|------------|
| `@dataclass` | Internal data, no validation needed | None | Mutable (default) |
| `Pydantic BaseModel` | External data (APIs, configs, user input) | Full | Immutable option |
| `NamedTuple` | Simple immutable records, dict interop | None | Immutable |
| `TypedDict` | Dict with known keys (JSON schemas) | Type hints only | Mutable |

```python
from dataclasses import dataclass
from typing import NamedTuple
from pydantic import BaseModel

# dataclass - internal, no validation
@dataclass
class CacheEntry:
    key: str
    value: bytes
    ttl: int = 3600

# Pydantic - external data needing validation
class UserInput(BaseModel):
    email: str  # Validates email format
    age: int    # Validates >= 0

# NamedTuple - simple immutable record
class Point(NamedTuple):
    x: float
    y: float
```

**Rule of thumb:** Start with `@dataclass`. Switch to Pydantic when you need validation.

### Environment Variables with Pydantic Settings

```python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GWT_",  # GWT_CREDENTIALS_PATH, GWT_LOG_LEVEL, etc.
    )

    credentials_path: Path = Path(".client_secret.json")
    token_path: Path = Path("tmp/token.json")
    target_directory: Path = Path("exports")
    use_keyring: bool = True
    log_level: str = "WARNING"
    log_format: str = "pretty"  # or "json"
```

**Usage:**

```bash
# Environment variable
export GWT_LOG_LEVEL=DEBUG

# .env file
GWT_TARGET_DIRECTORY=./my-exports
GWT_USE_KEYRING=false
```

### Domain Config with Pydantic BaseModel

```python
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ExporterConfig(BaseModel):
    """Configuration for the exporter (domain-specific)."""

    export_format: Literal["pdf", "docx", "md", "html"] = "html"
    link_depth: int = Field(default=0, ge=0, le=5)
    enable_frontmatter: bool = False
    spreadsheet_mode: Literal["combined", "separate", "csv"] = "combined"

    @field_validator("target_directory", mode="before")
    @classmethod
    def ensure_path(cls, v):
        """Coerce strings to Path objects."""
        return Path(v) if not isinstance(v, Path) else v
```

**Key distinction:**

- `Settings` (pydantic-settings): Environment/deployment config
- `ExporterConfig` (BaseModel): Domain/business logic config

---

## CLI Integration

For full CLI patterns, see **[agentic-cli.md](./agentic-cli.md)**. Key patterns:

### Dual-Mode Output (Human/JSON)

```python
from enum import Enum
from abc import ABC, abstractmethod


class OutputMode(str, Enum):
    HUMAN = "human"
    JSON = "json"


class BaseOutputFormatter(ABC):
    @abstractmethod
    def print_progress(self, message: str) -> None: ...
    @abstractmethod
    def print_success(self, message: str) -> None: ...
    @abstractmethod
    def print_error(self, message: str) -> None: ...
    @abstractmethod
    def print_result(self, result: CommandOutput) -> None: ...


class HumanOutputFormatter(BaseOutputFormatter):
    def __init__(self):
        self.console = Console()

    def print_success(self, message: str) -> None:
        self.console.print(f"[green]{message}[/green]")


class JSONOutputFormatter(BaseOutputFormatter):
    def print_success(self, message: str) -> None:
        pass  # Suppress in JSON mode

    def print_result(self, result: CommandOutput) -> None:
        print(result.model_dump_json(indent=2))


def get_formatter(mode: OutputMode) -> BaseOutputFormatter:
    """Factory for formatters (OCP in action)."""
    return JSONOutputFormatter() if mode == OutputMode.JSON else HumanOutputFormatter()
```

### Error Handler Context Manager

```python
from contextlib import contextmanager
from typing import Generator


@contextmanager
def cli_error_handler(
    formatter: BaseOutputFormatter,
    auth_hint: bool = True,
) -> Generator[None, None, None]:
    """Consistent error handling across CLI commands."""
    try:
        yield
    except FileNotFoundError as e:
        formatter.print_error(f"Error: {e}")
        if auth_hint:
            formatter.print_info("Run 'cmd credentials login' to authenticate")
        raise typer.Exit(1) from e
    except Exception as e:
        formatter.print_error(f"Error: {e}")
        raise typer.Exit(1) from e


# Usage in every command
@app.command()
def download(url: str):
    formatter = get_formatter(get_output_mode())
    with cli_error_handler(formatter):
        # Command logic here
        ...
```

---

## Testing Setup

### pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
addopts = "-v --tb=short --strict-markers"
testpaths = ["tests"]
markers = [
    "unit: Pure unit tests with no external dependencies",
    "integration: Tests that use mocked external services",
    "e2e: End-to-end CLI tests",
    "slow: Tests that take longer than 1 second",
]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]
```

### Fixture Patterns (conftest.py)

```python
import pytest
from pathlib import Path
from unittest.mock import MagicMock


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_credentials():
    """Mock Google OAuth credentials."""
    creds = MagicMock()
    creds.valid = True
    creds.expired = False
    return creds


@pytest.fixture
def mock_drive_service(mock_credentials):
    """Mock Google Drive API service."""
    service = MagicMock()
    service.files().get().execute.return_value = {
        "id": "test-id",
        "name": "Test Document",
        "mimeType": "application/vnd.google-apps.document",
    }
    return service
```

### CLI E2E Tests

```python
from typer.testing import CliRunner
from project_name.cli.app import app

runner = CliRunner()


class TestCLI:
    def test_help_shows_commands(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "download" in result.stdout

    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    @pytest.mark.e2e
    def test_download_requires_auth(self, mock_credentials_file):
        result = runner.invoke(app, ["download", "https://docs.google.com/..."])
        assert result.exit_code == 1
        assert "credentials" in result.stdout.lower()
```

---

## Quality Gates

### pyproject.toml (Ruff + MyPy)

```toml
[tool.ruff]
line-length = 120
src = ["src", "tests"]
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "PT", "SIM"]
ignore = ["B008"]  # Allow function calls in default args (Typer pattern)
fixable = ["ALL"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.16.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]
```

### Commands

```bash
# Install hooks
pre-commit install

# Run all checks
pre-commit run --all-files

# Individual tools
uv run ruff check --fix
uv run ruff format
uv run mypy src/
uv run pytest -v
uv run pytest --cov=src --cov-report=term-missing
```

---

## Entry Point Pattern

```python
# src/project_name/__init__.py
"""Project Name - Description."""

from .cli.app import app

__version__ = "0.1.0"
__all__ = ["app", "main"]


def main() -> None:
    """CLI entry point."""
    import sys
    from loguru import logger

    # Configure logging based on settings
    from .settings import Settings
    settings = Settings()

    logger.remove()
    if settings.log_format == "json":
        logger.add(sys.stderr, format="{message}", serialize=True)
    else:
        logger.add(sys.stderr, level=settings.log_level)

    try:
        app()
    except KeyboardInterrupt:
        print("\n[yellow]Cancelled by user[/yellow]", file=sys.stderr)
        sys.exit(130)
```

```toml
# pyproject.toml
[project.scripts]
cmd = "project_name:main"
```

---

## Summary Checklist

| Aspect | Pattern | Benefit |
|--------|---------|---------|
| **Structure** | src/ layout, core/cli separation | Testability, reusability |
| **SRP** | One class = one responsibility | Maintainability |
| **OCP** | ABC + factory functions | Extensibility |
| **LSP** | Honor interface contracts | Substitutability |
| **ISP** | Small interfaces (5-6 methods) | Simplicity |
| **DIP** | Depend on abstractions, lazy load | Flexibility, testability |
| **Config** | Pydantic + env vars | Validation, flexibility |
| **CLI** | Dual-mode output, error handler | UX, automation |
| **Testing** | Markers, fixtures, e2e | Coverage, confidence |
| **Quality** | ruff + mypy + pre-commit | Consistency |

---

## References

- [Agentic CLI Design Patterns](./agentic-cli.md) — CLI UX patterns for AI agents
- [Snapshot Testing](./snapshot-testing.md) — Approval testing with syrupy
- [uv Documentation](https://docs.astral.sh/uv/) — Fast Python package manager
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — Environment config
- [Typer Documentation](https://typer.tiangolo.com/) — CLI framework
