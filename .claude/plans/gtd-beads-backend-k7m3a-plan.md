# GTD Beads Backend Implementation (TDD) - Implementation Plan

**Status**: READY FOR IMPLEMENTATION
**Created**: 2026-02-26

## Summary

Implement the full GTDStorage interface for the Beads backend using `bd` CLI subprocess calls, following TDD red-green-refactor methodology. The stub from PR #27 has critical bugs (wrong base class name, wrong method signatures, constructor raises on missing bd, top-level import breaks CI). This plan fixes those issues and implements all 11 abstract methods with full test coverage using mocked subprocess calls.

## Files

> **Note**: This is the canonical file list. The `## Implementation Plan` section below references these same files with detailed implementation instructions.

### Files to Edit
- `skills/gtd/scripts/gtdlib/backends/__init__.py`
- `skills/gtd/scripts/gtdlib/backends/beads.py`
- `skills/gtd/scripts/gtdlib/config.py`
- `tests/gtd/test_config.py`

### Files to Create
- `tests/gtd/test_beads.py`

---

## Code Context

### Base class: GTDStorage (storage.py)
The abstract base class defines 11 abstract methods that must be implemented:
- `is_setup(self) -> bool` (line 193)
- `setup(self, verbose: bool = False, fix_drift: bool = False) -> None` (line 198)
- `create_item(self, title: str, labels: list[str], body: str | None = None, project: str | None = None) -> GTDItem` (line 220)
- `get_item(self, item_id: str) -> GTDItem | None` (line 231)
- `list_items(self, labels: list[str] | None = None, state: str = "open", project: str | None = None, limit: int = 100) -> list[GTDItem]` (line 236)
- `update_item(self, item_id: str, title: str | None = None, body: str | None = None, labels: list[str] | None = None, project: str | None = None) -> GTDItem` (line 247)
- `add_labels(self, item_id: str, labels: list[str]) -> GTDItem` (line 259)
- `remove_labels(self, item_id: str, labels: list[str]) -> GTDItem` (line 263)
- `close_item(self, item_id: str) -> GTDItem` (line 269)
- `reopen_item(self, item_id: str) -> GTDItem` (line 273)
- `add_comment(self, item_id: str, body: str) -> None` (line 279)

Plus convenience methods from base class: `capture()`, `list_inbox()`, `list_by_context()`.

### Reference backend: TaskwarriorStorage (taskwarrior.py)
Pattern to follow for Beads backend:
- `_run_task()` (line 38): subprocess wrapper with check/verbose flags
- `_label_to_tag()` / `_tag_to_label()` (lines 68-88): label conversion (GTD `context/focus` <-> TW `gtd_context_focus`)
- `_parse_task()` (line 136): JSON output -> GTDItem conversion
- Constructor takes config, does NOT check if tool is installed (line 21-29)
- `is_setup()` checks filesystem state (line 92-95)
- `setup()` creates local config files (line 97-134)

### Reference backend: GitHubStorage (github.py)
- `_run_gh()` (line 25): subprocess wrapper, similar pattern
- `_parse_issue()` (line 225): JSON -> GTDItem
- Uses `json.loads()` throughout for parsing CLI output

### Existing test patterns

**test_taskwarrior.py**: Integration tests with real CLI, skipped via `pytestmark = pytest.mark.skipif(shutil.which("task") is None, ...)`. Uses `tmp_path` fixture for isolation.

**test_config.py**: Imports `GitHubConfig, GTDConfig, TaskwarriorConfig, detect_skill_directory, load_config, save_config` from `gtdlib.config`. Tests loading/saving JSON config files with `tmp_path`.

### __init__.py pattern (backends/)
Current main branch: only exports `GitHubStorage` and `TaskwarriorStorage`.
Feature branch: adds top-level `from .beads import BeadsBackend` which breaks when bd is not installed because the constructor calls `_check_bd_available()` which calls subprocess.

### Config system (config.py)
- `AVAILABLE_BACKENDS = ["github", "taskwarrior"]` on main (feature branch adds "beads")
- `GTDConfig` dataclass with backend field and per-backend config dataclasses
- `load_config()` builds config defensively with try/except TypeError
- `save_config()` only serializes non-default backend-specific config

### bd CLI JSON formats (verified empirically)

**`bd create "title" --labels "a,b" --description "body" --json`** returns single object:
```json
{"id": "prefix-abc", "title": "...", "description": "...", "status": "open", "priority": 2, "issue_type": "task", "owner": "...", "created_at": "...", "updated_at": "...", "labels": ["a", "b"]}
```

**`bd create "title" --silent`** returns just the ID string: `prefix-abc`

**`bd list --json --label "gtd:context:focus" --status open --limit 50`** returns array:
```json
[{"id": "...", "title": "...", "status": "open", "labels": ["..."], "dependency_count": 0, "dependent_count": 0, "comment_count": 0, ...}]
```

**`bd show <id> --json`** returns array (even for single item):
```json
[{"id": "...", "title": "...", "description": "...", "status": "open", "labels": [...], ...}]
```

**`bd close <id> --json`** returns array with `closed_at` and `close_reason`:
```json
[{"id": "...", "status": "closed", "closed_at": "...", "close_reason": "Closed", ...}]
```

**`bd reopen <id> --json`** returns array, status back to "open".

**`bd update <id> --add-label "x" --remove-label "y" --set-labels "a,b" --title "new" --description "new" --json`** returns array.

**`bd comments <id> --json`** returns array:
```json
[{"id": 1, "issue_id": "...", "author": "...", "text": "...", "created_at": "..."}]
```

**`bd comments add <id> "text"`** returns text confirmation.

**`bd status --json`** can be used to check if bd is initialized.

**Native date fields**: `due_at` and `defer_until` are native bd fields, set via `--due` and `--defer` on create/update. No YAML frontmatter needed.

---

## External Context

### bd CLI Reference (from --help)

Key flags used:
- `bd create [title] --labels "a,b" --description "..." --due "2026-03-15" --defer "2026-03-01" --silent`
- `bd list --label "a" --status "open" --limit 50 --json`
- `bd show <id> --json`
- `bd update <id> --add-label "x" --remove-label "y" --set-labels "a,b" --title "new" --description "new" --due "..." --defer "..." --json`
- `bd close <id> --json`
- `bd reopen <id> --json`
- `bd comments <id> --json`
- `bd comments add <id> "text"`
- `bd label list-all --json` - list all unique labels
- `bd status --json` - database status check

Global flags: `--json`, `--quiet`, `--sandbox`

### Beads label format
GTD labels use colon-delimited format: `gtd:context:focus`, `gtd:status:active`, etc.
Non-GTD labels in beads are ignored when parsing.

---

## Architectural Narrative

### Task
Implement the full `GTDStorage` interface for the Beads backend. The existing PR #27 stub has critical issues that must be fixed first: wrong base class reference (`StorageBackend` instead of `GTDStorage`), wrong method signatures (don't match the abstract interface), constructor that raises on missing bd CLI, and a top-level import in `__init__.py` that breaks CI.

### Architecture
The GTD skill uses a strategy pattern: `GTDStorage` is the abstract base (storage.py:126), with concrete backends for GitHub (github.py), Taskwarrior (taskwarrior.py), and now Beads (beads.py). The config system (config.py) selects the active backend. All backends use subprocess calls to their respective CLI tools.

### Selected Context
- `skills/gtd/scripts/gtdlib/storage.py:126-304` - GTDStorage base class with all abstract method signatures
- `skills/gtd/scripts/gtdlib/backends/taskwarrior.py` - Reference implementation for CLI-based backend
- `skills/gtd/scripts/gtdlib/config.py` - Config loading/saving, needs beads support
- `skills/gtd/scripts/gtdlib/backends/__init__.py` - Package exports, needs lazy import
- `tests/gtd/test_taskwarrior.py` - Reference test patterns (skipif, fixtures, CRUD tests)
- `tests/gtd/test_config.py` - Config test patterns

### Relationships
```
config.py (GTDConfig.backend="beads") -> BeadsBackendConfig
backends/__init__.py -> lazy import BeadsStorage
beads.py (BeadsStorage) -> inherits GTDStorage (storage.py)
beads.py -> subprocess calls to bd CLI
test_beads.py -> imports BeadsStorage, mocks subprocess
test_config.py -> imports BeadsBackendConfig
```

### External Context
- bd CLI uses Dolt (Git-for-data) underneath. The `bd status` command checks if the database is initialized.
- Beads has native `due_at` and `defer_until` fields -- metadata does NOT need YAML frontmatter in descriptions. The PR #27 docs are wrong about this.
- `bd create --silent` returns just the ID, useful for scripting.
- `bd show` returns an array even for single items.
- Beads labels have no color/description metadata (unlike GitHub labels), so `get_label_drift()` returns `[]` (same as Taskwarrior).

### Implementation Notes

**Label mapping**: GTD `context/focus` <-> Beads `gtd:context:focus` (colon-separated, with `gtd:` prefix). This differs from Taskwarrior's underscore format (`gtd_context_focus`).

**Constructor pattern**: Do NOT call `_check_bd_available()` in constructor. Follow Taskwarrior pattern where constructor just stores config. Check availability in `is_setup()`.

**Lazy import in __init__.py**: Use a function `get_beads_backend_class()` or simply don't export BeadsStorage at package level. Import it only when backend="beads" is selected. This avoids import failures when bd is not installed.

**State mapping**: Beads uses `status: "open"|"closed"` which maps directly to GTD's `state: "open"|"closed"`. Beads also has `in_progress`, `blocked`, `deferred` statuses. For GTD list_items(state="open"), filter by `--status open`.

**Project mapping**: Beads doesn't have a native project/milestone concept like GitHub. Use a label convention: `project:<name>` label on beads issues. This keeps it simple and queryable with `--label "project:myproject"`.

**Metadata storage**: Beads has native `due_at` and `defer_until` fields. For `waiting_for` and `blocked_by`, store as JSON in the `--metadata` field of bd (which supports arbitrary JSON).

### Ambiguities

1. **Project support**: Beads has no native milestone/project. Decision: use `project:<name>` labels for now. This is simpler than metadata and allows filtering with `--label`.
2. **`get_comments()` not in base class**: The stub had `get_comments()` but `GTDStorage` has no such method. Decision: implement as a Beads-specific method (not abstract), useful but not required by the interface.
3. **`reopen_item()` mapping**: bd has `bd reopen <id>` which maps directly.
4. **`verbose` parameter**: `list_items` on GitHub/TW backends accept `verbose` kwarg not in the abstract signature. Decision: add `verbose: bool = False` as in sibling backends (extra kwarg is harmless).

### Requirements

1. All 11 abstract methods of GTDStorage implemented
2. No import errors when bd CLI is not installed
3. `is_setup()` returns False when bd is not available (not raise)
4. `setup()` provides helpful error message (bd requires manual init)
5. Label conversion round-trips correctly for all 12 GTD labels
6. Tests use mocked subprocess (don't require bd installed)
7. Config loading/saving works for beads backend
8. Existing GitHub and Taskwarrior backends unaffected
9. Tests follow existing patterns (pytest classes, fixtures, skipif where needed)
10. All tests pass, linting passes, no type errors

### Constraints

- Python 3.11+ (from pyproject.toml)
- Must use subprocess to call bd CLI (consistent with existing pattern)
- bd CLI is optional -- GTD must work without it installed
- Tests must not require bd installed (mock subprocess.run)
- Follow existing code style (ruff, 88 line length)

### Selected Approach

**Approach**: Mocked subprocess tests with full GTDStorage implementation

**Description**: Implement `BeadsStorage` (renamed from `BeadsBackend` to match naming convention -- `GitHubStorage`, `TaskwarriorStorage`, `BeadsStorage`) as a subclass of `GTDStorage`. All bd CLI interactions go through a `_run_bd()` helper method. Tests mock `subprocess.run` at the method level to simulate bd CLI responses. The `__init__.py` uses lazy import (only import when explicitly requested). The config system adds `BeadsBackendConfig` (intentionally empty, documented why) and updates `save_config` to handle it.

**Rationale**: Mocking subprocess is the established pattern for testing CLI-wrapping backends. It allows running tests in CI without bd installed. The existing Taskwarrior tests use real CLI (integration tests), but that's only possible because task is a simple binary. bd requires a Dolt server, making real integration tests impractical in CI.

**Trade-offs Accepted**: Mocked tests don't catch real bd CLI behavior changes. Mitigated by testing label conversion and JSON parsing as pure functions separately.

---

## Implementation Plan

### tests/gtd/test_beads.py [create]

**Purpose**: Full test suite for BeadsStorage backend with mocked subprocess calls.

**TOTAL CHANGES**: 1 (create entire file)

**Changes**:
1. Create new test file with classes covering all GTDStorage methods

**Implementation Details**:
- Import `BeadsStorage` from `gtdlib.backends.beads`
- Import `GTDStorage` from `gtdlib.storage`
- Mock `subprocess.run` to simulate bd CLI responses
- Test classes: `TestLabelConversion`, `TestIsSetup`, `TestSetup`, `TestCreateItem`, `TestGetItem`, `TestListItems`, `TestUpdateItem`, `TestAddRemoveLabels`, `TestCloseReopen`, `TestAddComment`, `TestGetComments`, `TestCapture`, `TestListInbox`, `TestListByContext`

**Reference Implementation**:
```python
"""Tests for BeadsStorage backend.

Unit tests using mocked subprocess calls. Does not require bd CLI installed.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from gtdlib.backends.beads import BeadsStorage
from gtdlib.config import BeadsBackendConfig
from gtdlib.storage import GTDStorage, StorageNotSetupError


# --- Helpers ---


def _mock_bd_result(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> MagicMock:
    """Create a mock subprocess.CompletedProcess."""
    result = MagicMock()
    result.stdout = stdout
    result.stderr = stderr
    result.returncode = returncode
    return result


def _bd_json(data: list | dict) -> str:
    """Serialize data to JSON string as bd CLI would output."""
    return json.dumps(data)


# Sample bd JSON responses
SAMPLE_BEAD = {
    "id": "GTD-abc",
    "title": "Buy milk",
    "description": "From the store",
    "status": "open",
    "priority": 2,
    "issue_type": "task",
    "owner": "user@example.com",
    "created_at": "2026-02-26T10:00:00Z",
    "created_by": "Test User",
    "updated_at": "2026-02-26T10:00:00Z",
    "labels": ["gtd:status:someday"],
}

SAMPLE_BEAD_WITH_LABELS = {
    "id": "GTD-def",
    "title": "Review PR",
    "description": "",
    "status": "open",
    "priority": 2,
    "issue_type": "task",
    "owner": "user@example.com",
    "created_at": "2026-02-26T10:00:00Z",
    "created_by": "Test User",
    "updated_at": "2026-02-26T10:00:00Z",
    "labels": [
        "gtd:context:focus",
        "gtd:energy:high",
        "gtd:status:active",
        "gtd:horizon:action",
    ],
}

SAMPLE_BEAD_CLOSED = {
    **SAMPLE_BEAD,
    "status": "closed",
    "closed_at": "2026-02-26T12:00:00Z",
    "close_reason": "Closed",
}


@pytest.fixture
def storage() -> BeadsStorage:
    """Create a BeadsStorage instance for testing."""
    return BeadsStorage(config=BeadsBackendConfig())


# --- Label Conversion ---


class TestLabelConversion:
    """Test GTD label <-> Beads label conversion."""

    def test_label_to_beads(self, storage: BeadsStorage):
        assert storage._label_to_beads("context/focus") == "gtd:context:focus"

    def test_label_to_beads_energy(self, storage: BeadsStorage):
        assert storage._label_to_beads("energy/high") == "gtd:energy:high"

    def test_beads_to_label(self, storage: BeadsStorage):
        assert storage._beads_to_label("gtd:context:focus") == "context/focus"

    def test_beads_to_label_non_gtd_returns_none(self, storage: BeadsStorage):
        assert storage._beads_to_label("ralph") is None

    def test_beads_to_label_malformed_returns_none(self, storage: BeadsStorage):
        assert storage._beads_to_label("gtd:") is None

    def test_beads_to_label_only_prefix_returns_none(self, storage: BeadsStorage):
        assert storage._beads_to_label("gtd:context") is None

    def test_roundtrip_all_labels(self, storage: BeadsStorage):
        """Every GTD label survives label -> beads -> label conversion."""
        for label in GTDStorage.get_all_labels():
            beads_label = storage._label_to_beads(label)
            assert storage._beads_to_label(beads_label) == label, (
                f"Roundtrip failed for {label}"
            )

    def test_labels_to_beads_list(self, storage: BeadsStorage):
        result = storage._labels_to_beads(["context/focus", "status/active"])
        assert result == ["gtd:context:focus", "gtd:status:active"]

    def test_parse_beads_labels_filters_non_gtd(self, storage: BeadsStorage):
        result = storage._parse_beads_labels(
            ["gtd:context:focus", "ralph", "project:myproj", "gtd:status:active"]
        )
        assert result == ["context/focus", "status/active"]


# --- Setup ---


class TestIsSetup:
    """Test is_setup() checks bd availability."""

    def test_is_setup_true_when_bd_available(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout='{"total": 5}')
            assert storage.is_setup() is True

    def test_is_setup_false_when_bd_not_found(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("bd not found")
            assert storage.is_setup() is False

    def test_is_setup_false_when_bd_fails(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                returncode=1, stderr="no database"
            )
            assert storage.is_setup() is False


class TestSetup:
    """Test setup() behavior."""

    def test_setup_when_bd_available_is_noop(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout='{"total": 5}')
            storage.setup(verbose=True)  # Should not raise

    def test_setup_when_bd_not_found_raises(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("bd not found")
            with pytest.raises(StorageNotSetupError, match="bd command not found"):
                storage.setup()

    def test_setup_when_bd_not_initialized_raises(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                returncode=1, stderr="no database found"
            )
            with pytest.raises(StorageNotSetupError, match="not initialized"):
                storage.setup()


# --- CRUD Operations ---


class TestCreateItem:
    """Test creating GTD items via bd create."""

    def test_create_simple_item(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            # First call: bd create --silent returns ID
            # Second call: bd show returns full item
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            item = storage.create_item(title="Buy milk", labels=["status/someday"])
            assert item.title == "Buy milk"
            assert item.id == "GTD-abc"
            assert item.state == "open"

            # Verify bd create was called with correct args
            create_call = mock_run.call_args_list[0]
            cmd = create_call[0][0]
            assert cmd[0] == "bd"
            assert cmd[1] == "create"
            assert "Buy milk" in cmd
            assert "--labels" in cmd
            labels_idx = cmd.index("--labels")
            assert "gtd:status:someday" in cmd[labels_idx + 1]
            assert "--silent" in cmd

    def test_create_item_with_body(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            item = storage.create_item(
                title="Buy milk",
                labels=["status/someday"],
                body="From the store",
            )
            create_call = mock_run.call_args_list[0]
            cmd = create_call[0][0]
            assert "--description" in cmd
            desc_idx = cmd.index("--description")
            assert cmd[desc_idx + 1] == "From the store"

    def test_create_item_with_project_label(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            bead_with_project = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:active", "project:website"],
            }
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([bead_with_project])),
            ]
            item = storage.create_item(
                title="Write docs",
                labels=["status/active"],
                project="website",
            )
            create_call = mock_run.call_args_list[0]
            cmd = create_call[0][0]
            labels_idx = cmd.index("--labels")
            assert "project:website" in cmd[labels_idx + 1]

    def test_create_item_with_multiple_labels(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-def\n"),
                _mock_bd_result(
                    stdout=_bd_json([SAMPLE_BEAD_WITH_LABELS])
                ),
            ]
            item = storage.create_item(
                title="Review PR",
                labels=[
                    "context/focus",
                    "energy/high",
                    "status/active",
                    "horizon/action",
                ],
            )
            assert "context/focus" in item.labels
            assert "energy/high" in item.labels
            assert "status/active" in item.labels
            assert "horizon/action" in item.labels


class TestGetItem:
    """Test retrieving items by ID."""

    def test_get_existing_item(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD])
            )
            item = storage.get_item("GTD-abc")
            assert item is not None
            assert item.title == "Buy milk"
            assert item.id == "GTD-abc"

    def test_get_nonexistent_item_returns_none(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                returncode=1, stderr="not found"
            )
            result = storage.get_item("GTD-zzz")
            assert result is None

    def test_get_item_parses_labels(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_WITH_LABELS])
            )
            item = storage.get_item("GTD-def")
            assert "context/focus" in item.labels
            assert "energy/high" in item.labels

    def test_get_item_parses_project_from_label(self, storage: BeadsStorage):
        bead_with_project = {
            **SAMPLE_BEAD,
            "labels": ["gtd:status:active", "project:website"],
        }
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([bead_with_project])
            )
            item = storage.get_item("GTD-abc")
            assert item.project == "website"

    def test_get_item_parses_closed_state(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_CLOSED])
            )
            item = storage.get_item("GTD-abc")
            assert item.state == "closed"
            assert item.closed_at == "2026-02-26T12:00:00Z"


class TestListItems:
    """Test listing/querying items."""

    def test_list_empty_returns_empty(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            items = storage.list_items()
            assert items == []

    def test_list_returns_items(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD, SAMPLE_BEAD_WITH_LABELS])
            )
            items = storage.list_items()
            assert len(items) == 2

    def test_list_filters_by_label(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_WITH_LABELS])
            )
            items = storage.list_items(labels=["status/active"])
            # Verify bd list was called with correct label filter
            cmd = mock_run.call_args[0][0]
            assert "--label" in cmd
            label_idx = cmd.index("--label")
            assert "gtd:status:active" in cmd[label_idx + 1]

    def test_list_filters_by_state_open(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            storage.list_items(state="open")
            cmd = mock_run.call_args[0][0]
            assert "--status" in cmd
            status_idx = cmd.index("--status")
            assert cmd[status_idx + 1] == "open"

    def test_list_filters_by_state_closed(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            storage.list_items(state="closed")
            cmd = mock_run.call_args[0][0]
            assert "--status" in cmd
            status_idx = cmd.index("--status")
            assert cmd[status_idx + 1] == "closed"

    def test_list_filters_by_project(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            storage.list_items(project="website")
            cmd = mock_run.call_args[0][0]
            assert "--label" in cmd
            # Should include project:website in labels
            label_indices = [i for i, x in enumerate(cmd) if x == "--label"]
            label_values = [cmd[i + 1] for i in label_indices]
            assert any("project:website" in v for v in label_values)

    def test_list_respects_limit(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            storage.list_items(limit=25)
            cmd = mock_run.call_args[0][0]
            assert "--limit" in cmd
            limit_idx = cmd.index("--limit")
            assert cmd[limit_idx + 1] == "25"


class TestUpdateItem:
    """Test updating existing items."""

    def test_update_title(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            updated_bead = {**SAMPLE_BEAD, "title": "New title"}
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # update
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # get_item
            ]
            item = storage.update_item("GTD-abc", title="New title")
            update_call = mock_run.call_args_list[0]
            cmd = update_call[0][0]
            assert "--title" in cmd
            title_idx = cmd.index("--title")
            assert cmd[title_idx + 1] == "New title"

    def test_update_labels_replaces_all(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            updated_bead = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:waiting", "gtd:context:meetings"],
            }
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # update
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # get_item
            ]
            item = storage.update_item(
                "GTD-abc",
                labels=["status/waiting", "context/meetings"],
            )
            update_call = mock_run.call_args_list[0]
            cmd = update_call[0][0]
            assert "--set-labels" in cmd

    def test_update_body(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            updated_bead = {**SAMPLE_BEAD, "description": "New body"}
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([updated_bead])),
                _mock_bd_result(stdout=_bd_json([updated_bead])),
            ]
            item = storage.update_item("GTD-abc", body="New body")
            update_call = mock_run.call_args_list[0]
            cmd = update_call[0][0]
            assert "--description" in cmd

    def test_update_project(self, storage: BeadsStorage):
        """Updating project adds project:<name> label."""
        with patch("subprocess.run") as mock_run:
            # First: get current item to find existing project label
            current_bead = {**SAMPLE_BEAD, "labels": ["gtd:status:someday"]}
            updated_bead = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:someday", "project:newproj"],
            }
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([current_bead])),  # get current
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # update
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # get_item
            ]
            item = storage.update_item("GTD-abc", project="newproj")
            assert item.project == "newproj"


class TestAddRemoveLabels:
    """Test incremental label management."""

    def test_add_labels(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            updated_bead = {
                **SAMPLE_BEAD,
                "labels": [
                    "gtd:status:someday",
                    "gtd:context:focus",
                    "gtd:energy:high",
                ],
            }
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # update
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # get_item
            ]
            item = storage.add_labels(
                "GTD-abc", ["context/focus", "energy/high"]
            )
            update_call = mock_run.call_args_list[0]
            cmd = update_call[0][0]
            assert "--add-label" in cmd

    def test_remove_labels(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            updated_bead = {
                **SAMPLE_BEAD_WITH_LABELS,
                "labels": ["gtd:energy:high", "gtd:status:active", "gtd:horizon:action"],
            }
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([updated_bead])),
                _mock_bd_result(stdout=_bd_json([updated_bead])),
            ]
            item = storage.remove_labels("GTD-def", ["context/focus"])
            update_call = mock_run.call_args_list[0]
            cmd = update_call[0][0]
            assert "--remove-label" in cmd


class TestCloseReopen:
    """Test closing and reopening items."""

    def test_close_item(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_CLOSED])),  # close
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_CLOSED])),  # get_item
            ]
            item = storage.close_item("GTD-abc")
            assert item.state == "closed"
            close_call = mock_run.call_args_list[0]
            cmd = close_call[0][0]
            assert cmd[:3] == ["bd", "close", "GTD-abc"]

    def test_reopen_item(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            reopened_bead = {**SAMPLE_BEAD}  # status: open
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([reopened_bead])),
                _mock_bd_result(stdout=_bd_json([reopened_bead])),
            ]
            item = storage.reopen_item("GTD-abc")
            assert item.state == "open"
            reopen_call = mock_run.call_args_list[0]
            cmd = reopen_call[0][0]
            assert cmd[:3] == ["bd", "reopen", "GTD-abc"]


class TestAddComment:
    """Test adding comments."""

    def test_add_comment(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout="Comment added to GTD-abc"
            )
            storage.add_comment("GTD-abc", "This is a note")
            cmd = mock_run.call_args[0][0]
            assert cmd == [
                "bd", "comments", "add", "GTD-abc", "This is a note"
            ]


class TestGetComments:
    """Test getting comments (Beads-specific, not in base class)."""

    def test_get_comments(self, storage: BeadsStorage):
        comments_json = [
            {
                "id": 1,
                "issue_id": "GTD-abc",
                "author": "Test User",
                "text": "First comment",
                "created_at": "2026-02-26T10:00:00Z",
            },
            {
                "id": 2,
                "issue_id": "GTD-abc",
                "author": "Test User",
                "text": "Second comment",
                "created_at": "2026-02-26T11:00:00Z",
            },
        ]
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json(comments_json)
            )
            comments = storage.get_comments("GTD-abc")
            assert len(comments) == 2
            assert comments[0]["text"] == "First comment"

    def test_get_comments_empty(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            comments = storage.get_comments("GTD-abc")
            assert comments == []


# --- Convenience Methods (from GTDStorage base class) ---


class TestCapture:
    """Test quick-capture to inbox via base class convenience method."""

    def test_capture_creates_someday_item(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            item = storage.capture("Quick thought")
            assert item.title == "Buy milk"  # From mock response
            # Verify create was called with status/someday label
            create_call = mock_run.call_args_list[0]
            cmd = create_call[0][0]
            labels_idx = cmd.index("--labels")
            assert "gtd:status:someday" in cmd[labels_idx + 1]


class TestListByContext:
    """Test context-based filtering via base class convenience method."""

    def test_list_by_context(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_WITH_LABELS])
            )
            items = storage.list_by_context("focus")
            assert len(items) == 1
            # Verify labels filter included context/focus and status/active
            cmd = mock_run.call_args[0][0]
            label_indices = [i for i, x in enumerate(cmd) if x == "--label"]
            label_values = [cmd[i + 1] for i in label_indices]
            all_labels = ",".join(label_values)
            assert "gtd:context:focus" in all_labels
            assert "gtd:status:active" in all_labels
```

**Dependencies**: `skills/gtd/scripts/gtdlib/backends/beads.py`, `skills/gtd/scripts/gtdlib/config.py`
**Provides**: Test coverage for BeadsStorage, validates all GTDStorage methods

---

### skills/gtd/scripts/gtdlib/backends/beads.py [edit]

**Purpose**: Full implementation of GTDStorage for Beads backend using bd CLI.

**TOTAL CHANGES**: 1 (complete rewrite of the stub)

**Changes**:
1. Replace entire file content (lines 1-182) with correct implementation inheriting from GTDStorage with correct method signatures

**Implementation Details**:
- Class name: `BeadsStorage` (matches `GitHubStorage`, `TaskwarriorStorage` naming)
- Base class: `GTDStorage` (not `StorageBackend` which doesn't exist)
- Constructor: `__init__(self, config: BeadsBackendConfig)` -- stores config, does NOT check bd availability
- `_run_bd(self, args: list[str], check: bool = True, verbose: bool = False) -> str` -- subprocess wrapper
- `_label_to_beads(self, label: str) -> str` -- `context/focus` -> `gtd:context:focus`
- `_beads_to_label(self, beads_label: str) -> str | None` -- reverse
- `_labels_to_beads(self, labels: list[str]) -> list[str]` -- batch conversion
- `_parse_beads_labels(self, beads_labels: list[str]) -> list[str]` -- filter and convert
- `_extract_project(self, beads_labels: list[str]) -> str | None` -- extract `project:X` label
- `_parse_bead(self, data: dict) -> GTDItem` -- JSON to GTDItem
- All 11 abstract methods with exact signatures matching GTDStorage

**Reference Implementation**:
```python
"""Beads backend for GTD storage using bd CLI.

Uses the Beads/Dolt system (bd command) for GTD task storage,
enabling offline-first task management with Git-based synchronization.

Requirements:
- bd CLI installed and initialized (bd init)
- Beads database configured in current workspace

Architecture:
- GTD labels map to Beads labels (context/focus -> gtd:context:focus)
- GTD metadata (due, defer) uses native bd fields (--due, --defer)
- waiting_for stored via bd --metadata JSON field
- Projects mapped to project:<name> labels
"""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from ..storage import GTDItem, GTDStorage, StorageNotSetupError

if TYPE_CHECKING:
    from ..config import BeadsBackendConfig


class BeadsStorage(GTDStorage):
    """GTD storage using Beads (bd CLI)."""

    def __init__(self, config: BeadsBackendConfig | None = None):
        """Initialize Beads storage.

        Args:
            config: Beads backend configuration. Currently empty as bd
                auto-discovers its .beads/ directory. Kept for interface
                consistency with other backends.
        """
        self.config = config

    def _run_bd(
        self, args: list[str], check: bool = True, verbose: bool = False
    ) -> str:
        """Run a bd command and return stdout.

        Args:
            args: Command arguments to pass to bd.
            check: If True, raise RuntimeError on non-zero exit code.
            verbose: If True, print the command being run.

        Returns:
            stdout from the command.

        Raises:
            RuntimeError: If check=True and command fails.
            FileNotFoundError: If bd binary is not installed.
        """
        cmd = ["bd"] + args
        if verbose:
            print(f"  [DEBUG] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            if check:
                raise RuntimeError(f"bd command failed: {result.stderr}")
            return ""
        return result.stdout

    # --- Label Conversion ---

    def _label_to_beads(self, label: str) -> str:
        """Convert GTD label to Beads label format.

        Example: context/focus -> gtd:context:focus
        """
        category, value = label.split("/", 1)
        return f"gtd:{category}:{value}"

    def _beads_to_label(self, beads_label: str) -> str | None:
        """Convert Beads label to GTD label format.

        Example: gtd:context:focus -> context/focus
        Returns None if not a GTD label.
        """
        if not beads_label.startswith("gtd:"):
            return None
        parts = beads_label.split(":", 2)
        if len(parts) != 3 or not parts[1] or not parts[2]:
            return None
        return f"{parts[1]}/{parts[2]}"

    def _labels_to_beads(self, labels: list[str]) -> list[str]:
        """Convert a list of GTD labels to Beads format."""
        return [self._label_to_beads(label) for label in labels]

    def _parse_beads_labels(self, beads_labels: list[str]) -> list[str]:
        """Extract GTD labels from a list of Beads labels.

        Filters out non-GTD labels (e.g., project:X, custom labels).
        """
        gtd_labels = []
        for beads_label in beads_labels:
            label = self._beads_to_label(beads_label)
            if label is not None:
                gtd_labels.append(label)
        return gtd_labels

    def _extract_project(self, beads_labels: list[str]) -> str | None:
        """Extract project name from Beads labels.

        Looks for labels matching 'project:<name>'.
        Returns the first project found, or None.
        """
        for label in beads_labels:
            if label.startswith("project:"):
                return label.split(":", 1)[1]
        return None

    # --- Parsing ---

    def _parse_bead(self, data: dict) -> GTDItem:
        """Parse bd JSON output into GTDItem.

        Maps Beads fields to GTD fields:
        - id -> id
        - title -> title
        - description -> body
        - status (open/closed) -> state
        - labels with gtd: prefix -> labels
        - labels with project: prefix -> project
        - created_at -> created_at
        - closed_at -> closed_at
        """
        beads_labels = data.get("labels", []) or []
        gtd_labels = self._parse_beads_labels(beads_labels)
        project = self._extract_project(beads_labels)

        # Map beads status to GTD state
        status = data.get("status", "open")
        state = "closed" if status == "closed" else "open"

        return GTDItem(
            id=data["id"],
            title=data.get("title", ""),
            body=data.get("description") or None,
            state=state,
            labels=gtd_labels,
            project=project,
            url=None,  # Beads has no URL concept
            created_at=data.get("created_at"),
            closed_at=data.get("closed_at"),
        )

    # --- GTDStorage Implementation ---

    def is_setup(self) -> bool:
        """Check if bd CLI is available and a Beads database exists."""
        try:
            self._run_bd(["status", "--json"], check=True)
            return True
        except (RuntimeError, FileNotFoundError):
            return False

    def setup(self, verbose: bool = False, fix_drift: bool = False) -> None:
        """Verify Beads is set up. Raises if bd is not available.

        Beads requires manual initialization via 'bd init'. This method
        checks availability and provides guidance if not set up.

        Args:
            verbose: If True, print progress messages.
            fix_drift: Ignored for Beads (labels have no color/description).

        Raises:
            StorageNotSetupError: If bd is not installed or not initialized.
        """
        try:
            self._run_bd(["status", "--json"], check=True)
            if verbose:
                print("Beads backend is ready.")
        except FileNotFoundError:
            raise StorageNotSetupError(
                "bd command not found. Install the Beads CLI first: "
                "https://github.com/kortina/beads"
            )
        except RuntimeError as e:
            raise StorageNotSetupError(
                f"Beads database not initialized. Run 'bd init' first. "
                f"Error: {e}"
            )

    def create_item(
        self,
        title: str,
        labels: list[str],
        body: str | None = None,
        project: str | None = None,
    ) -> GTDItem:
        """Create a new GTD item in Beads.

        Args:
            title: Item title.
            labels: GTD labels (e.g., ["status/active", "context/focus"]).
            body: Optional description text.
            project: Optional project name (stored as project:<name> label).

        Returns:
            Created GTDItem.
        """
        beads_labels = self._labels_to_beads(labels)
        if project:
            beads_labels.append(f"project:{project}")

        args = ["create", title, "--labels", ",".join(beads_labels), "--silent"]
        if body:
            args.extend(["--description", body])

        # bd create --silent returns just the ID
        output = self._run_bd(args)
        item_id = output.strip()

        return self.get_item(item_id)

    def get_item(self, item_id: str) -> GTDItem | None:
        """Get a single item by ID.

        Args:
            item_id: Beads issue ID (e.g., "GTD-abc").

        Returns:
            GTDItem or None if not found.
        """
        try:
            output = self._run_bd(["show", item_id, "--json"])
            data = json.loads(output)
            # bd show returns an array even for single items
            if isinstance(data, list):
                if not data:
                    return None
                return self._parse_bead(data[0])
            return self._parse_bead(data)
        except (RuntimeError, json.JSONDecodeError):
            return None

    def list_items(
        self,
        labels: list[str] | None = None,
        state: str = "open",
        project: str | None = None,
        limit: int = 100,
        verbose: bool = False,
    ) -> list[GTDItem]:
        """List items matching criteria.

        Args:
            labels: Filter by GTD labels (AND logic -- must have ALL).
            state: Filter by state: "open" or "closed".
            project: Filter by project name.
            limit: Maximum number of results.
            verbose: If True, print debug output.

        Returns:
            List of matching GTDItems.
        """
        args = ["list", "--json", "--limit", str(limit)]

        if state in ("open", "closed"):
            args.extend(["--status", state])

        # Build label filters
        all_labels: list[str] = []
        if labels:
            all_labels.extend(self._labels_to_beads(labels))
        if project:
            all_labels.append(f"project:{project}")

        for label in all_labels:
            args.extend(["--label", label])

        output = self._run_bd(args, check=False, verbose=verbose)
        if not output.strip():
            return []

        try:
            data = json.loads(output)
            items = [self._parse_bead(bead) for bead in data]
            if verbose:
                print(f"  [DEBUG] Got {len(items)} items from Beads")
            return items
        except json.JSONDecodeError:
            return []

    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        body: str | None = None,
        labels: list[str] | None = None,
        project: str | None = None,
    ) -> GTDItem:
        """Update an existing item.

        Args:
            item_id: Beads issue ID.
            title: New title (or None to keep current).
            body: New description (or None to keep current).
            labels: New complete label set (replaces all GTD labels).
            project: New project name (or None to keep current).

        Returns:
            Updated GTDItem.
        """
        args = ["update", item_id, "--json"]

        if title is not None:
            args.extend(["--title", title])
        if body is not None:
            args.extend(["--description", body])

        if labels is not None:
            beads_labels = self._labels_to_beads(labels)
            # When setting labels, we need to preserve non-GTD labels
            # and replace only the GTD ones. Use --set-labels with full set.
            current = self.get_item(item_id)
            if current:
                # Get current non-GTD beads labels
                current_output = self._run_bd(
                    ["show", item_id, "--json"], check=False
                )
                try:
                    current_data = json.loads(current_output)
                    if isinstance(current_data, list) and current_data:
                        current_beads_labels = current_data[0].get("labels", []) or []
                    else:
                        current_beads_labels = []
                except json.JSONDecodeError:
                    current_beads_labels = []

                # Keep non-GTD labels, replace GTD labels
                non_gtd_labels = [
                    bl for bl in current_beads_labels
                    if not bl.startswith("gtd:")
                ]
                # If project is being set, remove old project: labels too
                if project is not None:
                    non_gtd_labels = [
                        bl for bl in non_gtd_labels
                        if not bl.startswith("project:")
                    ]
                all_beads_labels = non_gtd_labels + beads_labels
                if project is not None:
                    all_beads_labels.append(f"project:{project}")
                elif current and current.project:
                    all_beads_labels.append(f"project:{current.project}")
                args.extend(["--set-labels", ",".join(all_beads_labels)])
            else:
                args.extend(["--set-labels", ",".join(beads_labels)])
        elif project is not None:
            # Only updating project, not labels
            current = self.get_item(item_id)
            if current:
                current_output = self._run_bd(
                    ["show", item_id, "--json"], check=False
                )
                try:
                    current_data = json.loads(current_output)
                    if isinstance(current_data, list) and current_data:
                        current_beads_labels = current_data[0].get("labels", []) or []
                    else:
                        current_beads_labels = []
                except json.JSONDecodeError:
                    current_beads_labels = []
                # Remove old project: labels, add new one
                updated_labels = [
                    bl for bl in current_beads_labels
                    if not bl.startswith("project:")
                ]
                if project:
                    updated_labels.append(f"project:{project}")
                args.extend(["--set-labels", ",".join(updated_labels)])

        self._run_bd(args)
        return self.get_item(item_id)

    def add_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Add labels to an item.

        Args:
            item_id: Beads issue ID.
            labels: GTD labels to add.

        Returns:
            Updated GTDItem.
        """
        args = ["update", item_id, "--json"]
        for label in labels:
            args.extend(["--add-label", self._label_to_beads(label)])
        self._run_bd(args)
        return self.get_item(item_id)

    def remove_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Remove labels from an item.

        Args:
            item_id: Beads issue ID.
            labels: GTD labels to remove.

        Returns:
            Updated GTDItem.
        """
        args = ["update", item_id, "--json"]
        for label in labels:
            args.extend(["--remove-label", self._label_to_beads(label)])
        self._run_bd(args, check=False)
        return self.get_item(item_id)

    def close_item(self, item_id: str) -> GTDItem:
        """Close/complete an item.

        Args:
            item_id: Beads issue ID.

        Returns:
            Updated GTDItem with state="closed".
        """
        self._run_bd(["close", item_id, "--json"])
        return self.get_item(item_id)

    def reopen_item(self, item_id: str) -> GTDItem:
        """Reopen a closed item.

        Args:
            item_id: Beads issue ID.

        Returns:
            Updated GTDItem with state="open".
        """
        self._run_bd(["reopen", item_id, "--json"])
        return self.get_item(item_id)

    def add_comment(self, item_id: str, body: str) -> None:
        """Add a comment to an item.

        Args:
            item_id: Beads issue ID.
            body: Comment text.
        """
        self._run_bd(["comments", "add", item_id, body])

    # --- Beads-specific methods (not in base class) ---

    def get_comments(self, item_id: str) -> list[dict]:
        """Get comments for an item.

        Args:
            item_id: Beads issue ID.

        Returns:
            List of comment dicts with: id, issue_id, author, text, created_at.
        """
        try:
            output = self._run_bd(["comments", item_id, "--json"])
            data = json.loads(output)
            return data if isinstance(data, list) else []
        except (RuntimeError, json.JSONDecodeError):
            return []

    # --- Label introspection (inherited stubs) ---

    def get_existing_labels(self) -> set[str]:
        """Get GTD labels that exist in the Beads database."""
        try:
            output = self._run_bd(["label", "list-all", "--json"], check=False)
            if not output.strip():
                return set()
            data = json.loads(output)
            labels: set[str] = set()
            all_beads_labels = data if isinstance(data, list) else []
            for beads_label in all_beads_labels:
                # Handle both string and dict formats
                label_str = beads_label if isinstance(beads_label, str) else beads_label.get("name", "")
                gtd_label = self._beads_to_label(label_str)
                if gtd_label:
                    labels.add(gtd_label)
            return labels
        except (RuntimeError, json.JSONDecodeError):
            return set()

    def get_stale_labels(self) -> list[str]:
        """Find GTD-prefixed labels not in the canonical taxonomy."""
        existing = self.get_existing_labels()
        required = self.get_required_labels()
        prefixes = self.get_label_prefixes()

        stale = []
        for label in existing:
            if any(label.startswith(prefix) for prefix in prefixes):
                if label not in required:
                    stale.append(label)
        return sorted(stale)

    def get_label_drift(self) -> list[dict]:
        """Beads labels have no color/description, so drift is N/A."""
        return []

    def delete_label(self, name: str) -> bool:
        """Remove a GTD label from all items that have it.

        Args:
            name: GTD label name (e.g., "context/focus").

        Returns:
            True if the label was found and removed, False otherwise.
        """
        beads_label = self._label_to_beads(name)
        try:
            # Find items with this label
            output = self._run_bd(
                ["list", "--json", "--label", beads_label, "--limit", "0"],
                check=False,
            )
            if not output.strip():
                return False
            items = json.loads(output)
            if not items:
                return False
            for item in items:
                self._run_bd(
                    ["update", item["id"], "--remove-label", beads_label],
                    check=False,
                )
            return True
        except (RuntimeError, json.JSONDecodeError):
            return False
```

**Migration Pattern**:
```python
# BEFORE (stub lines 1-182):
from ..storage import GTDItem, StorageBackend, StorageNotSetupError
class BeadsBackend(StorageBackend):
    def __init__(self, config: BeadsBackendConfig):
        self.config = config
        self._check_bd_available()  # Raises on missing bd!
    def add_item(self, title, labels, body=None) -> GTDItem:  # Wrong signature
        raise NotImplementedError(...)

# AFTER:
from ..storage import GTDItem, GTDStorage, StorageNotSetupError
class BeadsStorage(GTDStorage):
    def __init__(self, config: BeadsBackendConfig | None = None):
        self.config = config  # No bd check in constructor
    def create_item(self, title, labels, body=None, project=None) -> GTDItem:  # Correct signature
        # Full implementation
```

**Dependencies**: `skills/gtd/scripts/gtdlib/storage.py` (GTDStorage base class), `skills/gtd/scripts/gtdlib/config.py` (BeadsBackendConfig)
**Provides**: `BeadsStorage` class with full GTDStorage implementation, label conversion methods (`_label_to_beads`, `_beads_to_label`, `_labels_to_beads`, `_parse_beads_labels`), `get_comments()` method

---

### skills/gtd/scripts/gtdlib/backends/__init__.py [edit]

**Purpose**: Package exports for GTD storage backends. Must not fail when bd is not installed.

**TOTAL CHANGES**: 1

**Changes**:
1. Replace top-level `from .beads import BeadsBackend` with lazy import (lines 1-6)

**Implementation Details**:
- Keep `GitHubStorage` and `TaskwarriorStorage` as top-level imports (they don't call external CLIs on import)
- Do NOT import BeadsStorage at top level
- Add a `get_backend_class(name: str)` function that imports on demand
- Update `__all__` to include `BeadsStorage` name but don't import it

**Reference Implementation**:
```python
"""GTD storage backends.

Backend classes:
- GitHubStorage: GitHub Issues via gh CLI
- TaskwarriorStorage: Taskwarrior via task CLI
- BeadsStorage: Beads via bd CLI (lazy import to avoid failure when bd not installed)
"""

from .github import GitHubStorage
from .taskwarrior import TaskwarriorStorage

__all__ = ["GitHubStorage", "TaskwarriorStorage", "BeadsStorage"]


def get_backend_class(name: str):
    """Get backend class by name. Supports lazy loading.

    Args:
        name: Backend name ("github", "taskwarrior", "beads").

    Returns:
        The backend class.

    Raises:
        ValueError: If name is not a valid backend.
    """
    if name == "github":
        return GitHubStorage
    elif name == "taskwarrior":
        return TaskwarriorStorage
    elif name == "beads":
        from .beads import BeadsStorage

        return BeadsStorage
    else:
        raise ValueError(f"Unknown backend: {name!r}")
```

**Migration Pattern**:
```python
# BEFORE (feature branch):
from .beads import BeadsBackend  # Fails if bd not installed!
from .github import GitHubStorage
from .taskwarrior import TaskwarriorStorage
__all__ = ["BeadsBackend", "GitHubStorage", "TaskwarriorStorage"]

# AFTER:
from .github import GitHubStorage
from .taskwarrior import TaskwarriorStorage
__all__ = ["GitHubStorage", "TaskwarriorStorage", "BeadsStorage"]
def get_backend_class(name: str): ...
```

**Dependencies**: `skills/gtd/scripts/gtdlib/backends/beads.py`
**Provides**: `get_backend_class(name: str)` function, lazy `BeadsStorage` access

---

### skills/gtd/scripts/gtdlib/config.py [edit]

**Purpose**: Add Beads backend to config system. The feature branch already added this, but we need to also update `save_config()` to handle beads and the return value of `load_config()` to include beads.

**TOTAL CHANGES**: 3

**Changes**:
1. Add `"beads"` to `AVAILABLE_BACKENDS` list (line 12, already done on feature branch)
2. Add `BeadsBackendConfig` dataclass with docstring explaining why it's empty (after line 22, already done on feature branch)
3. Add `beads` field to `GTDConfig` dataclass (after line 34, already done on feature branch)

These changes are already on the feature branch. The implementation here formalizes the exact code. On main branch, the edits are needed at:

**Changes on main branch config.py (line references for main branch)**:
1. Line 12: Add "beads" to AVAILABLE_BACKENDS
2. After line 22 (GitHubConfig): Add BeadsBackendConfig dataclass
3. Line 28 (GTDConfig): Add beads field
4. Lines 97-104 (load_config): Add beads_data parsing and BeadsBackendConfig construction
5. Line 135 (return GTDConfig): Add beads=beads_config parameter
6. Lines 177-183 (save_config): Add beads backend serialization (currently no non-default fields, so nothing to serialize)

**Reference Implementation**:

For `AVAILABLE_BACKENDS` (line 12):
```python
AVAILABLE_BACKENDS = ["github", "taskwarrior", "beads"]
```

For `BeadsBackendConfig` (after GitHubConfig):
```python
@dataclass
class BeadsBackendConfig:
    """Beads backend configuration.

    Currently empty: bd auto-discovers its .beads/ directory and config.
    This dataclass exists for interface consistency with other backends
    and to allow future configuration options (e.g., custom db path).
    """

    pass
```

For `GTDConfig` (add field):
```python
@dataclass
class GTDConfig:
    """GTD skill configuration."""

    backend: Literal["github", "taskwarrior", "beads"] = "github"
    taskwarrior: TaskwarriorConfig = field(default_factory=TaskwarriorConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    beads: BeadsBackendConfig = field(default_factory=BeadsBackendConfig)
```

For `load_config` (add beads parsing):
```python
    beads_data = data.get("beads", {})
    if not isinstance(beads_data, dict):
        beads_data = {}

    try:
        beads_config = BeadsBackendConfig(**beads_data)
    except TypeError:
        beads_config = BeadsBackendConfig()

    return GTDConfig(
        backend=backend,
        taskwarrior=tw_config,
        github=gh_config,
        beads=beads_config,
    )
```

For `save_config` (add beads case -- currently no non-default fields):
```python
    # Only include backend-specific config if non-default
    if config.backend == "taskwarrior":
        if config.taskwarrior.data_dir != ".gtd/taskwarrior":
            data["taskwarrior"] = {"data_dir": config.taskwarrior.data_dir}
    elif config.backend == "github":
        if config.github.repo:
            data["github"] = {"repo": config.github.repo}
    # beads: no non-default config to serialize (bd auto-discovers)
```

**Dependencies**: None (standalone config module)
**Provides**: `BeadsBackendConfig` dataclass, beads support in `load_config()` / `save_config()`, `AVAILABLE_BACKENDS` includes "beads"

---

### tests/gtd/test_config.py [edit]

**Purpose**: Add tests for beads backend config loading/saving.

**TOTAL CHANGES**: 3

**Changes**:
1. Add `BeadsBackendConfig` to imports (line 7)
2. Add `test_load_valid_beads_config` test method in TestLoadConfig class (after line 58)
3. Add `test_save_beads_config` test method in TestSaveConfig class (after line 115)

**Implementation Details**:

**Reference Implementation** (additions only):

Import addition (line 7):
```python
from gtdlib.config import (
    BeadsBackendConfig,
    GitHubConfig,
    GTDConfig,
    TaskwarriorConfig,
    detect_skill_directory,
    load_config,
    save_config,
)
```

New test in TestLoadConfig (after line 58):
```python
    def test_load_valid_beads_config(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"backend": "beads"}))
        config = load_config(config_file)
        assert config.backend == "beads"
        assert isinstance(config.beads, BeadsBackendConfig)
```

New tests in TestSaveConfig (after line 115):
```python
    def test_save_beads_config(self, tmp_path):
        path = tmp_path / "config.json"
        config = GTDConfig(backend="beads")
        save_config(config, path)
        data = json.loads(path.read_text())
        assert data == {"backend": "beads"}

    def test_roundtrip_beads_config(self, tmp_path):
        path = tmp_path / "config.json"
        original = GTDConfig(backend="beads")
        save_config(original, path)
        loaded = load_config(path)
        assert loaded.backend == "beads"
```

**Migration Pattern**:
```python
# BEFORE (line 7):
from gtdlib.config import (
    GitHubConfig,
    GTDConfig,
    TaskwarriorConfig,
    detect_skill_directory,
    load_config,
    save_config,
)

# AFTER:
from gtdlib.config import (
    BeadsBackendConfig,
    GitHubConfig,
    GTDConfig,
    TaskwarriorConfig,
    detect_skill_directory,
    load_config,
    save_config,
)
```

**Dependencies**: `skills/gtd/scripts/gtdlib/config.py` (BeadsBackendConfig)
**Provides**: Test coverage for beads config loading/saving

---

## Dependency Graph

> Converters use this to build `dependsOn` (prd.json) or `depends_on` (beads).
> Files in the same phase can execute in parallel. Later phases depend on earlier ones.

| Phase | File | Action | Depends On |
|-------|------|--------|------------|
| 1 | `skills/gtd/scripts/gtdlib/config.py` | edit | -- |
| 1 | `skills/gtd/scripts/gtdlib/backends/beads.py` | edit | -- |
| 2 | `skills/gtd/scripts/gtdlib/backends/__init__.py` | edit | `skills/gtd/scripts/gtdlib/backends/beads.py` |
| 2 | `tests/gtd/test_config.py` | edit | `skills/gtd/scripts/gtdlib/config.py` |
| 2 | `tests/gtd/test_beads.py` | create | `skills/gtd/scripts/gtdlib/backends/beads.py`, `skills/gtd/scripts/gtdlib/config.py` |

---

## Exit Criteria

### Test Commands
```bash
uv run pytest tests/gtd/test_beads.py -v     # Beads backend tests
uv run pytest tests/gtd/test_config.py -v     # Config tests including beads
uv run pytest tests/gtd/ -v                   # All GTD tests
uv run ruff check --fix && uv run ruff format # Lint + format
```

### Success Conditions
- [ ] All tests pass (exit code 0) including new test_beads.py and updated test_config.py
- [ ] No linting errors (exit code 0)
- [ ] `from gtdlib.backends import GitHubStorage, TaskwarriorStorage` works without bd installed
- [ ] `from gtdlib.backends import get_backend_class` works and `get_backend_class("beads")` returns BeadsStorage
- [ ] BeadsStorage implements all 11 abstract methods of GTDStorage
- [ ] Label conversion round-trips for all 12 GTD labels
- [ ] `import gtdlib` does not fail when bd is not installed (no top-level beads import)
- [ ] Existing test_taskwarrior.py and test_storage.py still pass
- [ ] All requirements from ### Requirements satisfied

### Verification Script
```bash
uv run pytest tests/gtd/ -v && uv run ruff check && uv run ruff format --check
```
