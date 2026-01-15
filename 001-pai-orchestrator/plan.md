# Implementation Plan: Layton (Personal AI Assistant)

**Branch**: `001-pai-orchestrator` | **Date**: 2026-01-13 | **Spec**: [spec.md](spec.md)

## Summary

Layton is a personal AI assistant skill named after Elizabeth Layton, Churchill's wartime secretary. The architecture cleanly separates:

- **SKILL.md** = Probabilistic work (AI judgment, synthesis, persona)
- **CLI** = Deterministic work (data ops, skill discovery, capture routing)
- **State** = Managed by [Beads](https://github.com/steveyegge/beads) (git-backed graph for AI agents)

## Technical Context

| Aspect | Value |
|--------|-------|
| **Language/Version** | Python 3.11 (matching project standard) |
| **Dependencies** | None (skill infrastructure; CLIs via subprocess) |
| **CLI Framework** | Typer (type-hints-driven, auto-validation) |
| **Storage** | `.layton/config.json` (structured) + `.layton/preferences.md` (prose) |
| **State Management** | Beads (git-backed, no custom JSON state) |
| **Testing** | pytest with syrupy snapshots |
| **Platform** | macOS/Linux (Claude Code environment) |
| **Performance** | <60s for morning briefing (SC-001) |

## Architecture: The Secretary Model

```
┌─────────────────────────────────────────────────────────────────┐
│       SKILL.md (Probabilistic - Elizabeth Layton's Judgment)    │
│  • Interprets user intent ("What should I work on?")            │
│  • Decides when to query which skills                           │
│  • Synthesizes information into coherent briefings              │
│  • Applies persona voice (calm, efficient, anticipating needs)  │
│  • Routes requests to appropriate workflows                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ invokes for data
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               CLI (Deterministic - Routine Operations)          │
│  • layton gather     → Discover and query available skills      │
│  • layton context    → Current context (time, work hours)       │
│  • layton note       → Route capture to appropriate skill       │
│  • layton config     → User preferences and personality         │
│  • layton doctor     → Health check and validation              │
└──────────────────────────┬──────────────────────────────────────┘
                           │ state via
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Beads (State Management)                      │
│  • Current focus/context as beads                               │
│  • History/audit trail in .beads/                               │
│  • Git-backed, no custom schema migration needed                │
│  • Designed for AI agent workflows                              │
└─────────────────────────────────────────────────────────────────┘
```

## Constitution Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Agentic by Design | ✅ Pass | CLI non-interactive; `--fix` hidden; `next_steps` in output |
| II. Determinism First | ✅ Pass | CLI handles data ops; SKILL.md handles AI synthesis |
| III. Test-First | ⚠️ Gate | Tests required before implementation (Phase 2) |
| IV. Simple > Clever | ✅ Pass | Sequential queries; Beads for state (no custom schema) |

## Key Design Decisions

### 1. CLI is Skill-Agnostic

The CLI discovers skills at runtime. It doesn't hardcode GTD, PARA, etc.

```python
def discover_skills() -> list[str]:
    """Find available skills at runtime."""
    skill_dirs = [Path("./skills"), Path("./.claude/skills")]
    # Return skills with SKILL.md and scripts/
```

### 2. State Management via Beads

**Removed from Layton:**

- `.layton/state.json` — No custom state files
- Schema migrations — Beads handles versioning
- History tracking — Beads has audit trail

**Kept in Layton:**

- `.layton/config.json` — Personal configuration only

### 3. Deterministic vs Probabilistic Split

| Operation | Type | Handler |
|-----------|------|---------|
| Query available skills | Deterministic | CLI `gather` |
| Get current time context | Deterministic | CLI `context` |
| Capture a note | Deterministic | CLI `note` |
| Synthesize a briefing | Probabilistic | SKILL.md workflow |
| Decide urgency of item | Probabilistic | SKILL.md workflow |
| Entity correlation | Probabilistic | SKILL.md workflow |

### 4. Attention References: Secretary's Notepad

User can say "track JIRA-1234 for me" and Layton creates an Attention Reference bead. Key principle: **store the reference and Layton's annotations, NOT cached data from source systems.**

See [data-model.md](data-model.md#attention-references-secretarys-notepad) for bead structure and lifecycle (FR-023 through FR-027).

### 5. Output Formatting Strategy

CLI supports dual output modes via formatter abstraction:

```python
from abc import ABC, abstractmethod

class BaseOutputFormatter(ABC):
    """Abstract base for output formatting."""

    @abstractmethod
    def format_briefing(self, briefing: dict) -> str: ...

    @abstractmethod
    def format_context(self, context: dict) -> str: ...

    @abstractmethod
    def format_error(self, error: dict) -> str: ...

class HumanFormatter(BaseOutputFormatter):
    """Rich-formatted terminal output with colors and tables."""

class JsonFormatter(BaseOutputFormatter):
    """Structured JSON for automation and LLM consumption."""
```

CLI uses `--json` global flag to switch formatters:

```python
@app.callback()
def main(json_output: bool = typer.Option(False, "--json")):
    ctx.obj["formatter"] = JsonFormatter() if json_output else HumanFormatter()
```

## Project Structure

### Documentation

```
specs/001-pai-orchestrator/
├── plan.md              # This file
├── research.md          # R1-R5 decisions
├── data-model.md        # Config schema only (state via Beads)
├── quickstart.md        # Usage guide
├── contracts/
│   └── cli-contract.md  # Deterministic CLI commands
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code

```
skills/layton/
├── SKILL.md              # Probabilistic: persona, routing, workflows
├── references/
│   └── persona.md        # Elizabeth Layton background
├── workflows/
│   ├── morning-briefing.md
│   ├── focus-suggestion.md
│   ├── cross-system-query.md
│   └── periodic-review.md
└── scripts/
    ├── layton            # CLI entrypoint (thin, ~100 lines)
    └── laytonlib/        # Internal package
        ├── __init__.py   # Public API exports
        ├── models.py     # Pydantic models, enums
        ├── config.py     # Config loading/validation
        ├── discovery.py  # Skill discovery
        ├── formatters/   # Output formatting
        │   ├── base.py   # Abstract formatter
        │   ├── human.py  # Rich terminal
        │   └── json.py   # JSON output
        └── services/     # Business logic
            ├── context.py
            ├── gather.py
            └── capture.py

tests/layton/
├── unit/
│   ├── test_context.py
│   ├── test_config.py
│   └── test_skill_discovery.py
├── integration/
│   └── test_skill_invocation.py
└── contract/
    └── test_cli_output.py

.layton/                  # Repo-local (gitignore-able)
├── config.json           # Structured settings (JSON)
└── preferences.md        # Behavioral instructions (prose)

.beads/                   # State management
└── (managed by Beads)
```

## Beads Testing Strategy

Integration tests use **temp directory isolation** (pattern from [speckit-to-beads](https://github.com/durandom/agentic/tree/main/beads/examples/speckit-to-beads)):

| Test Type | Strategy | Fixture |
|-----------|----------|---------|
| Unit tests | Mock `bd` subprocess calls | `mock_beads_cli` |
| Integration tests | Real `bd` CLI, isolated temp directory | `beads_test_dir` |

**How it works:**

1. `beads_test_dir` fixture creates `tmp_path/.beads` and sets `BEADS_DIR` env var
2. Runs `bd init` in temp directory to initialize isolated database
3. Tests execute against real `bd` CLI, validating actual Beads behavior
4. Temp directory auto-cleaned by pytest after test run

**Pollution prevention:**

```python
# In conftest.py
def pytest_configure(config):
    """Fail fast if tests would pollute production .beads/"""
    beads_dir = os.environ.get("BEADS_DIR", "")
    if beads_dir and not beads_dir.startswith(tempfile.gettempdir()):
        pytest.exit("BEADS_DIR must point to temp directory in tests")
```

See tasks T006a and T033a in [tasks.md](tasks.md) for implementation details.

## Snapshot Testing Patterns

Following the [snapshot-testing recipe](../../recipes/snapshot-testing.md), Layton tests use three levels:

### Level 1: Raw Snapshots (CLI Contract Tests)

Basic syrupy snapshots for deterministic CLI JSON output structure.

```python
def test_cli_gather_output(snapshot):
    result = subprocess.run(["layton", "gather"], capture_output=True)
    assert json.loads(result.stdout) == snapshot
```

### Level 2: Printers (Briefing Outputs)

Custom formatters that filter out noisy fields (timestamps, IDs) while preserving testable structure.

```python
def print_briefing(briefing: dict) -> str:
    """Format briefing for snapshot testing, filtering dynamic fields."""
    return f"""
=== Morning Briefing ===
Tasks Due: {len(briefing.get('tasks', []))}
Calendar Events: {len(briefing.get('events', []))}
Attention Items: {len(briefing.get('attention', []))}
Focus: {briefing.get('focus', {}).get('category', 'none')}
Top Priority: {briefing.get('tasks', [{}])[0].get('title', 'none') if briefing.get('tasks') else 'none'}
"""

def test_morning_briefing_structure(snapshot, mock_skills):
    briefing = layton_briefing(mock_skills)
    assert print_briefing(briefing) == snapshot
```

### Level 3: Storyboards (State Evolution)

Record sequences of interactions to test behavior across Beads state changes.

```python
def test_capture_appears_in_next_briefing(snapshot, beads_test_dir, mock_skills):
    """Storyboard: captured note surfaces in next morning briefing."""
    story = []

    # Scene 1: Initial state
    story.append("=== Day 1 Morning ===")
    story.append(print_briefing(layton_briefing(mock_skills)))

    # Scene 2: User captures a note
    story.append("=== User Capture ===")
    story.append("layton note 'Follow up with Sarah on budget review'")
    layton_note("Follow up with Sarah on budget review")

    # Scene 3: Next day briefing should reflect capture
    story.append("=== Day 2 Morning ===")
    story.append(print_briefing(layton_briefing(mock_skills)))

    assert "\n".join(story) == snapshot
```

**When to use each level:**

- **Level 1**: CLI output format validation (T009, T028)
- **Level 2**: Briefing/context output with dynamic fields
- **Level 3**: Multi-interaction scenarios, Attention Reference lifecycle (T033a)

## Mock Skill Response Factory

Tests use a `MockSkillResponseFactory` class to generate realistic skill responses:

```python
class MockSkillResponseFactory:
    """Factory for realistic skill query responses."""

    @staticmethod
    def gtd_tasks(count: int = 3, with_urgent: bool = True) -> dict:
        """Generate GTD task list response."""
        tasks = [{"id": f"task-{i}", "title": f"Task {i}", "status": "active"}
                 for i in range(count)]
        if with_urgent:
            tasks[0]["labels"] = ["urgent", "high-energy"]
        return {"success": True, "data": {"tasks": tasks}}

    @staticmethod
    def calendar_events(date: str = "today", count: int = 2) -> dict:
        """Generate calendar events with attendees."""
        return {"success": True, "data": {"events": [...]}}

    @staticmethod
    def beads_attention_ref(system: str = "jira", status: str = "tracking") -> dict:
        """Generate attention reference bead structure."""
        return {"system": system, "id": f"{system.upper()}-1234", "status": status}

    @staticmethod
    def skill_error(code: str, message: str) -> dict:
        """Generate error response structure."""
        return {"success": False, "error": {"code": code, "message": message}}
```

**Benefits:**

- Realistic multi-skill test scenarios
- Consistent test data across unit/integration tests
- Pairs with Printer pattern (factory creates data, printer formats it)

## Code Organization Guidelines

### Package Structure

Following established patterns in this repo (meeting-notes, gtd, the-day):

```
skills/layton/scripts/
├── layton                    # CLI entrypoint (Typer app)
└── laytonlib/                # Internal package
    ├── __init__.py           # Public API only (__all__)
    ├── models.py             # Pydantic models, dataclasses, enums
    ├── config.py             # Config loading/validation
    ├── discovery.py          # Skill discovery logic
    ├── formatters/           # Output formatting (SRP)
    │   ├── __init__.py
    │   ├── base.py           # Abstract BaseOutputFormatter
    │   ├── human.py          # Rich terminal output
    │   └── json.py           # Machine-readable JSON
    └── services/             # Business logic (one responsibility per file)
        ├── __init__.py
        ├── context.py        # Temporal context calculation
        ├── gather.py         # Skill query orchestration
        └── capture.py        # Note routing logic
```

### Python Best Practices

| Principle | Guideline |
|-----------|-----------|
| **Single Responsibility** | One class/module = one reason to change. `discovery.py` finds skills; `gather.py` queries them. |
| **Open/Closed** | Use abstract base classes (formatters) so new output formats don't modify existing code. |
| **Dependency Inversion** | High-level modules (CLI) depend on abstractions (BaseOutputFormatter), not concretions. |
| **File Size Target** | 200-400 lines per file. Split at 500+ lines (existing repo max ~550). |
| **Explicit Exports** | Every `__init__.py` defines `__all__` with public API only. |

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Package | `lowercase` | `laytonlib` |
| Module | `snake_case` | `skill_discovery.py` |
| Class | `PascalCase` | `SkillDiscovery` |
| Function | `snake_case` | `discover_skills()` |
| Constant | `UPPER_SNAKE` | `DEFAULT_TIMEOUT` |
| Private | `_prefix` | `_build_query()` |

### Patterns from google-workspace-tools

Adopted from [google-workspace-tools](https://github.com/rhdh/sidekick/google-workspace-tools):

| Pattern | Application in Layton |
|---------|----------------------|
| **Output formatter abstraction** | `BaseOutputFormatter` → `HumanFormatter`, `JsonFormatter` |
| **Context vars for output mode** | Thread-safe output mode without parameter threading |
| **Pydantic for config** | Type-safe config with validation in `config.py` |
| **Factory functions** | `get_formatter(json_mode: bool) -> BaseOutputFormatter` |

### What NOT to Do

- ❌ Don't put all logic in `layton` CLI file (keep it thin, ~100 lines)
- ❌ Don't use globals for state (pass dependencies explicitly)
- ❌ Don't mix I/O with business logic (services return data, CLI prints)
- ❌ Don't hardcode skill names (discover at runtime)

## Phase 0 Artifacts (Completed)

- [x] `research.md` — R1: Sequential queries, R2: Config storage, R3: CLI patterns, R4: Beads, R5: Skill interaction

## Phase 1 Artifacts (Completed)

- [x] `data-model.md` — Simplified to config only
- [x] `contracts/cli-contract.md` — 5 commands: gather, context, note, config, doctor
- [x] `quickstart.md` — Architecture, CLI usage, SKILL.md workflows

## CLI Contract Summary

| Command | Purpose |
|---------|---------|
| `layton gather` | Discover and query available skills |
| `layton context` | Get temporal context (time of day, work hours) |
| `layton note "<text>"` | Route capture to appropriate skill |
| `layton config` | Manage personal configuration |
| `layton doctor` | Validate setup and skill availability |
| `layton preferences` | Manage behavioral instructions (prose) |

**Not in CLI** (handled by SKILL.md):

- Morning briefing
- Focus suggestion
- Cross-system query
- Periodic reviews
- Attention item surfacing

## Next Steps

Run `/speckit.tasks` to generate implementation tasks from this plan.
