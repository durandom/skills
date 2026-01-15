# Layton Stage 0: Design Document

## Context

This is Stage 0 of a multi-stage implementation. The original planning (`001-pai-orchestrator/`) encompassed GTD, Calendar, Jira, Email, and Slack integration. That scope is too ambitious for initial delivery.

Stage 0 proves the core architecture:

- **Beads** as the "notepad" (mutable state management)
- **`.layton/`** as the "filing cabinet" (stable configuration)
- **Thin CLI** for deterministic operations only

### Current State

- Beads (`bd` CLI) is a mature tool for AI-native task tracking
- No Layton skill exists yet (greenfield)
- Planning documents exist in `001-pai-orchestrator/` and `.planning/layton.md`

### Constraints

- Must work without AI for all CLI operations (deterministic)
- Must integrate with existing skills/commands directory structure
- Cannot duplicate Beads functionality (no `layton track` command)

## Goals / Non-Goals

**Goals:**

- Verify Beads is available and working (`layton doctor`)
- Provide temporal context for SKILL.md workflows (`layton context`)
- Enable personal configuration management (`layton config`)
- Establish conventions for how Layton uses Beads (tags, description format)

**Non-Goals:**

- AI synthesis or probabilistic operations (Stage 2+)
- Skill discovery and aggregation (Stage 1)
- Morning briefings or focus suggestions (Stage 2+)
- Recipe system for learned patterns (Stage 3+)
- Cross-system entity correlation (Stage 4+)

## Decisions

### Decision 1: Beads as sole state store

**Choice**: Use Beads for ALL mutable state; no `.layton/state.json`

**Alternatives considered**:

- Custom state files in `.layton/` — rejected: duplicates Beads, loses its git-based conflict resolution
- Hybrid approach — rejected: adds complexity, unclear when to use which

**Rationale**: Beads provides typed dependencies, ready-work detection, branch scoping, and JSON output. Building custom state management would replicate these features poorly.

### Decision 2: Config as simple key-value store (no schema validation)

**Choice**: `.layton/config.json` is a loose JSON file; any valid JSON is accepted

**Alternatives considered**:

- Pydantic schema validation — rejected for Stage 0: over-engineered for 3 keys
- JSON Schema validation — rejected: adds dependency, users own their config
- Typed config with strict fields — rejected: limits user customization

**Rationale**: Stage 0 only needs `timezone`, `work.schedule.start`, `work.schedule.end`. A loose schema lets users add their own keys without CLI changes. Strict validation can be added later if needed.

### Decision 3: No runtime default merging

**Choice**: If a config key is missing, fail with clear error rather than silently using defaults

**Alternatives considered**:

- Merge defaults at runtime — rejected: hides configuration issues, makes debugging harder
- Fall back to environment variables — rejected: adds another config source to manage

**Rationale**: Explicit failure is better than implicit behavior. Users run `layton config init` once to get defaults, then own their configuration. This follows the principle of "fail fast, fail clearly."

### Decision 4: CLI follows agentic patterns

**Choice**: No-arg defaults, hidden destructive flags, `next_steps` in all responses

**Patterns applied**:

- `layton` → runs `layton doctor` (useful no-arg default)
- `layton config` → runs `layton config show` (safe default)
- `layton doctor --fix` is hidden but suggested in `next_steps`
- All `--json` output includes `success`, `next_steps` fields

**Rationale**: AI agents parse CLI output; humans want sensible defaults. Hidden destructive flags prevent accidental data loss while remaining discoverable.

### Decision 5: Simple labels over state machine

**Choice**: Use `bd create ... -l watching,layton` instead of `bd state` machine

**Alternatives considered**:

- Beads state machine (`bd state`) — deferred: overkill for Stage 0, adds complexity
- Multiple label taxonomies — rejected: simple is better for now

**Rationale**: Stage 0 only needs `watching`, `focus`, and `layton` labels. State machine pattern adds transitions, guards, and history tracking that aren't needed yet. Can evolve to state machine in Stage 3+ if warranted.

### Decision 6: Python implementation using existing patterns

**Choice**: Python CLI using uv, matching other skills (GTD)

**Alternatives considered**:

- Bash script — rejected: too limited for config management and JSON handling
- TypeScript/Bun — rejected: this repo uses Python for CLI tools

**Rationale**: Consistency with existing `gtd` skill and build infrastructure. Uses Typer for CLI, Pydantic for models (when needed).

**References**: [python-project-architecture.md](../../../../recipes/python-project-architecture.md) — flat package pattern

### Decision 7: Dual-mode output (human/JSON)

**Choice**: All commands support `--json` flag with consistent response structure

**Pattern applied** (from [agentic-cli.md](../../../../recipes/agentic-cli.md)):

- Human output: Rich formatting, colors, readable tables
- JSON output: Machine-parseable with `success`, `data`, `error`, `next_steps` fields
- Single `OutputFormatter` abstraction handles both modes

**Rationale**: AI agents need structured JSON; humans want pretty output. The formatter abstraction (OCP) allows adding new output modes later without changing command logic.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **Beads is hard dependency** | `layton doctor` checks early and fails clearly. Installation docs will cover Beads setup. |
| **No AI capability in Stage 0** | This is intentional - Stage 0 proves the foundation. SKILL.md (Stage 1+) adds AI synthesis. |
| **Config schema may need to change** | Loose schema means no breaking changes; users own their config structure. |
| **Time-of-day boundaries are arbitrary** | Based on common patterns; boundaries are configurable via SKILL.md if needed later. |
| **Only one focus bead** | SKILL.md enforces this convention; CLI doesn't validate. Trust the AI workflow. |

## Implementation Approach

### Directory Structure

Follows flat package pattern from [python-project-architecture.md](../../../../recipes/python-project-architecture.md):

```
skills/layton/
├── SKILL.md                  # Placeholder for Stage 1
├── scripts/
│   └── layton                # CLI entrypoint (thin wrapper)
└── laytonlib/                # Flat package
    ├── __init__.py           # Package init, exports public API
    ├── __main__.py           # Enables: python -m laytonlib
    ├── cli.py                # Typer app with commands
    ├── core.py               # Business logic (no CLI deps)
    ├── config.py             # Config loading (key-value store)
    ├── context.py            # Temporal context
    ├── doctor.py             # Health checks
    └── formatters.py         # OutputFormatter (human/JSON)

tests/layton/                 # Test directory mirrors source
├── conftest.py               # Shared fixtures
├── unit/                     # Fast, isolated tests
│   ├── test_config.py
│   └── test_context.py
└── e2e/                      # CLI integration tests
    └── test_cli.py

.layton/                      # Per-repo config (gitignore-able)
└── config.json
```

**Key separation**: `core.py` contains pure business logic (temporal classification, config parsing); `cli.py` is a thin wrapper that imports from core. This enables testing core logic without CLI.

### Command Implementation Order

1. **`layton doctor`** — validates setup, establishes testing pattern
2. **`layton config init`** — creates config file for other commands
3. **`layton config show/keys/get/set`** — config management
4. **`layton context`** — temporal context (depends on config)

### Testing Strategy

Follows patterns from [snapshot-testing.md](../../../../recipes/snapshot-testing.md) and [python-project-architecture.md](../../../../recipes/python-project-architecture.md):

**Test markers** (pytest):

- `@pytest.mark.unit` — Fast, isolated tests (config parsing, temporal classification)
- `@pytest.mark.e2e` — CLI integration tests via `CliRunner`

**Snapshot testing** (syrupy):

- **Level 1** (raw): Snapshot `layton context --json` output directly
- **Level 2** (printer): Format doctor check results for readable diffs
- Use `AmberSnapshotExtension` for multi-line output

**Test isolation** (CRITICAL):

- Tests MUST NOT touch real `.beads/` or `.layton/` directories
- Use `tmp_path` fixture for all file-based tests
- For Beads integration tests, use `--db` flag or `--sandbox` mode
- Verify isolation with `bd info --json` showing temp path

**Fixtures** (`conftest.py`):

```python
@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Fully isolated environment with temp .layton/ and .beads/."""
    # Create isolated directories
    layton_dir = tmp_path / ".layton"
    layton_dir.mkdir()
    beads_dir = tmp_path / ".beads"
    beads_dir.mkdir()

    # Change working directory to temp (isolates bd auto-detection)
    monkeypatch.chdir(tmp_path)

    return tmp_path

@pytest.fixture
def temp_config(isolated_env):
    """Temporary .layton/config.json for isolated tests."""
    config_path = isolated_env / ".layton" / "config.json"
    return config_path

@pytest.fixture
def mock_beads_available(monkeypatch):
    """Mock bd CLI availability check (unit tests only)."""
    monkeypatch.setattr(shutil, "which", lambda cmd: "/usr/bin/bd" if cmd == "bd" else None)

@pytest.fixture
def real_beads_isolated(isolated_env):
    """Real bd CLI in isolated temp directory (integration tests)."""
    # bd will auto-init in isolated_env/.beads/ on first write
    return isolated_env / ".beads"
```

**E2E tests** (CliRunner):

```python
from typer.testing import CliRunner
runner = CliRunner()

def test_doctor_no_beads(isolated_env, monkeypatch):
    """Test doctor fails gracefully when bd CLI is missing."""
    monkeypatch.setattr(shutil, "which", lambda cmd: None)  # No bd
    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 2
    assert "beads_available" in result.stdout

def test_doctor_with_beads(isolated_env, real_beads_isolated):
    """Test doctor passes with bd available in isolated env."""
    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0  # or 1 if config missing (fixable)
```

## Open Questions

1. **Default timezone**: Should `layton config init` detect system timezone or use UTC?
   - *Recommendation*: Detect via `datetime.now().astimezone().tzinfo` or fallback to UTC.

2. **Config file permissions**: Should `.layton/` be added to `.gitignore` automatically?
   - *Recommendation*: No — let users decide. Document in SKILL.md quickstart.

3. **Beads initialization**: Should `layton doctor --fix` also run `bd init` if needed?
   - *Recommendation*: No — Beads init is a separate concern. Suggest in `next_steps`.
