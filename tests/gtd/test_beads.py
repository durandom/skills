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
            mock_run.return_value = _mock_bd_result(returncode=1, stderr="no database")
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
            storage.create_item(
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
            website_epic = {**SAMPLE_EPIC, "id": "GTD-epic1", "title": "website"}
            bead_with_project = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:active", "project:website"],
            }
            mock_run.side_effect = [
                # ensure_project → get_milestone → _list_epics_raw
                _mock_bd_result(stdout=_bd_json([website_epic])),
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([bead_with_project])),
            ]
            storage.create_item(
                title="Write docs",
                labels=["status/active"],
                project="website",
            )
            create_call = mock_run.call_args_list[1]
            cmd = create_call[0][0]
            labels_idx = cmd.index("--labels")
            assert "project:website" in cmd[labels_idx + 1]

    def test_create_item_with_project_sets_parent(self, storage: BeadsStorage):
        """Creating an item with project must pass --parent <epic-id> to bd create."""
        with patch("subprocess.run") as mock_run:
            website_epic = {**SAMPLE_EPIC, "id": "GTD-epic1", "title": "website"}
            bead_with_project = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:active", "project:website"],
            }
            mock_run.side_effect = [
                # ensure_project → get_milestone → _list_epics_raw
                _mock_bd_result(stdout=_bd_json([website_epic])),
                # bd create --silent
                _mock_bd_result(stdout="GTD-abc\n"),
                # bd show (get_item)
                _mock_bd_result(stdout=_bd_json([bead_with_project])),
            ]
            storage.create_item(
                title="Write docs",
                labels=["status/active"],
                project="website",
            )
            create_call = mock_run.call_args_list[1]
            cmd = create_call[0][0]
            assert "--parent" in cmd
            parent_idx = cmd.index("--parent")
            assert cmd[parent_idx + 1] == "GTD-epic1"

    def test_create_item_with_multiple_labels(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-def\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_LABELS])),
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

    def test_create_item_adds_gtd_label(self, storage: BeadsStorage):
        """All items created via GTD skill should have gtd label."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            storage.create_item(title="Test task", labels=["status/active"])
            create_call = mock_run.call_args_list[0]
            cmd = create_call[0][0]
            labels_idx = cmd.index("--labels")
            labels_str = cmd[labels_idx + 1]
            assert "gtd" in labels_str.split(",")


class TestGetItem:
    """Test retrieving items by ID."""

    def test_get_existing_item(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD]))
            item = storage.get_item("GTD-abc")
            assert item is not None
            assert item.title == "Buy milk"
            assert item.id == "GTD-abc"

    def test_get_nonexistent_item_returns_none(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(returncode=1, stderr="not found")
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
            storage.list_items(labels=["status/active"])
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
            storage.update_item("GTD-abc", title="New title")
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
                # _get_current_beads_labels (show)
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # update
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # get_item
            ]
            storage.update_item(
                "GTD-abc",
                labels=["status/waiting", "context/meetings"],
            )
            update_call = mock_run.call_args_list[1]
            cmd = update_call[0][0]
            assert "--set-labels" in cmd

    def test_update_body(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            updated_bead = {**SAMPLE_BEAD, "description": "New body"}
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([updated_bead])),
                _mock_bd_result(stdout=_bd_json([updated_bead])),
            ]
            storage.update_item("GTD-abc", body="New body")
            update_call = mock_run.call_args_list[0]
            cmd = update_call[0][0]
            assert "--description" in cmd

    def test_update_project(self, storage: BeadsStorage):
        """Updating project adds project:<name> label."""
        with patch("subprocess.run") as mock_run:
            current_bead = {**SAMPLE_BEAD, "labels": ["gtd:status:someday"]}
            updated_bead = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:someday", "project:newproj"],
            }
            newproj_epic = {**SAMPLE_EPIC, "id": "GTD-epic2", "title": "newproj"}
            mock_run.side_effect = [
                # ensure_project → get_milestone → _list_epics_raw
                _mock_bd_result(stdout=_bd_json([newproj_epic])),
                # _get_current_beads_labels
                _mock_bd_result(stdout=_bd_json([current_bead])),
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # update
                _mock_bd_result(stdout=_bd_json([updated_bead])),  # get_item
            ]
            item = storage.update_item("GTD-abc", project="newproj")
            assert item.project == "newproj"

    def test_update_project_sets_parent(self, storage: BeadsStorage):
        """Updating project must pass --parent <epic-id> to bd update."""
        with patch("subprocess.run") as mock_run:
            current_bead = {**SAMPLE_BEAD, "labels": ["gtd:status:someday"]}
            updated_bead = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:someday", "project:newproj"],
            }
            newproj_epic = {**SAMPLE_EPIC, "id": "GTD-epic2", "title": "newproj"}
            mock_run.side_effect = [
                # ensure_project → get_milestone → _list_epics_raw
                _mock_bd_result(stdout=_bd_json([newproj_epic])),
                # _get_current_beads_labels
                _mock_bd_result(stdout=_bd_json([current_bead])),
                # bd update
                _mock_bd_result(stdout=_bd_json([updated_bead])),
                # _get_item_or_raise (show)
                _mock_bd_result(stdout=_bd_json([updated_bead])),
            ]
            storage.update_item("GTD-abc", project="newproj")
            update_call = mock_run.call_args_list[2]
            cmd = update_call[0][0]
            assert "--parent" in cmd
            parent_idx = cmd.index("--parent")
            assert cmd[parent_idx + 1] == "GTD-epic2"


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
            storage.add_labels("GTD-abc", ["context/focus", "energy/high"])
            update_call = mock_run.call_args_list[0]
            cmd = update_call[0][0]
            assert "--add-label" in cmd

    def test_remove_labels(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            updated_bead = {
                **SAMPLE_BEAD_WITH_LABELS,
                "labels": [
                    "gtd:energy:high",
                    "gtd:status:active",
                    "gtd:horizon:action",
                ],
            }
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([updated_bead])),
                _mock_bd_result(stdout=_bd_json([updated_bead])),
            ]
            storage.remove_labels("GTD-def", ["context/focus"])
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
            mock_run.return_value = _mock_bd_result(stdout="Comment added to GTD-abc")
            storage.add_comment("GTD-abc", "This is a note")
            cmd = mock_run.call_args[0][0]
            assert cmd == [
                "bd",
                "comments",
                "add",
                "GTD-abc",
                "This is a note",
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
            mock_run.return_value = _mock_bd_result(stdout=_bd_json(comments_json))
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


# ---------------------------------------------------------------------------
# Feature: Native due/defer fields (durandom-skills-ugr)
# ---------------------------------------------------------------------------

# Sample bead with native due_at / defer_until fields from bd JSON
SAMPLE_BEAD_WITH_DUE = {
    **SAMPLE_BEAD,
    "due_at": "2026-03-15T00:00:00Z",
    "defer_until": "2026-03-10T00:00:00Z",
}


class TestCreateItemWithDue:
    """Test create_item passes --due and --defer flags to bd."""

    def test_create_with_due_date(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])),
            ]
            storage.create_item(
                title="Pay bill",
                labels=["status/active"],
                due="2026-03-15",
            )
            create_call = mock_run.call_args_list[0]
            cmd = create_call[0][0]
            assert "--due" in cmd
            due_idx = cmd.index("--due")
            assert cmd[due_idx + 1] == "2026-03-15"

    def test_create_with_defer(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])),
            ]
            storage.create_item(
                title="Review later",
                labels=["status/someday"],
                defer_until="2026-03-10",
            )
            create_call = mock_run.call_args_list[0]
            cmd = create_call[0][0]
            assert "--defer" in cmd
            defer_idx = cmd.index("--defer")
            assert cmd[defer_idx + 1] == "2026-03-10"

    def test_create_without_due_omits_flag(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            storage.create_item(title="No deadline", labels=["status/someday"])
            cmd = mock_run.call_args_list[0][0][0]
            assert "--due" not in cmd
            assert "--defer" not in cmd


class TestUpdateItemWithDue:
    """Test update_item passes --due and --defer flags."""

    def test_update_due(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])),  # update
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])),  # get_item
            ]
            storage.update_item("GTD-abc", due="2026-03-15")
            cmd = mock_run.call_args_list[0][0][0]
            assert "--due" in cmd
            assert cmd[cmd.index("--due") + 1] == "2026-03-15"

    def test_update_defer(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])),
            ]
            storage.update_item("GTD-abc", defer_until="2026-03-10")
            cmd = mock_run.call_args_list[0][0][0]
            assert "--defer" in cmd
            assert cmd[cmd.index("--defer") + 1] == "2026-03-10"


class TestParseDueFromBeadsJSON:
    """Test that native due_at/defer_until from bd JSON populate GTDItem.due."""

    def test_parse_due_at_into_item_due(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])
            )
            item = storage.get_item("GTD-abc")
            assert item is not None
            assert item.due is not None
            assert item.due.isoformat() == "2026-03-15"

    def test_parse_defer_until_into_item(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_WITH_DUE])
            )
            item = storage.get_item("GTD-abc")
            assert item is not None
            assert item.defer_until is not None
            assert item.defer_until.isoformat() == "2026-03-10"

    def test_no_due_at_means_none(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD]))
            item = storage.get_item("GTD-abc")
            assert item.due is None
            assert item.defer_until is None

    def test_due_at_utc_timestamp_converts_to_local_date(self, storage: BeadsStorage):
        """due_at is converted to local date, not naively sliced as UTC string.

        bd stores due_at in UTC. A user in UTC+1 (CET) setting "2026-03-03" causes
        bd to store "2026-03-02T23:00:00Z". Naively taking [:10] yields "2026-03-02"
        (wrong: one day off). We must convert to local date first.
        """
        from datetime import date as date_type, datetime

        due_at_utc = "2026-03-02T23:00:00Z"
        # Compute expected date via proper UTC→local conversion (same as the fix)
        expected = (
            datetime.fromisoformat("2026-03-02T23:00:00+00:00")
            .astimezone(tz=None)
            .date()
        )
        bead = {**SAMPLE_BEAD, "due_at": due_at_utc}
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([bead]))
            item = storage.get_item("GTD-abc")
            assert item.due == expected
            # In timezones > UTC, the local date must differ from naive UTC slice
            import time

            utc_offset_hours = -time.timezone / 3600
            naive_slice = date_type.fromisoformat(due_at_utc[:10])  # "2026-03-02"
            if utc_offset_hours > 0:
                assert item.due != naive_slice, (
                    "Timezone off-by-one bug: due date was naively sliced as UTC "
                    f"({naive_slice}) instead of converted to local date ({expected})"
                )


class TestListItemsWithDueFilters:
    """Test list_items passes --overdue and --due-before flags."""

    def test_list_overdue(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            storage.list_items(overdue=True)
            cmd = mock_run.call_args[0][0]
            assert "--overdue" in cmd

    def test_list_due_before(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            storage.list_items(due_before="2026-03-31")
            cmd = mock_run.call_args[0][0]
            assert "--due-before" in cmd
            assert cmd[cmd.index("--due-before") + 1] == "2026-03-31"

    def test_no_due_filter_omits_flag(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout="[]")
            storage.list_items()
            cmd = mock_run.call_args[0][0]
            assert "--overdue" not in cmd
            assert "--due-before" not in cmd


# ---------------------------------------------------------------------------
# Feature: JSON metadata for waiting_for/blocked_by (durandom-skills-i23)
# ---------------------------------------------------------------------------

SAMPLE_BEAD_WITH_METADATA = {
    **SAMPLE_BEAD,
    "metadata": {"waiting_for": {"person": "Alice", "reason": "Design mockups"}},
}

SAMPLE_BEAD_WITH_BLOCKED = {
    **SAMPLE_BEAD,
    "metadata": {"blocked_by": [42, 43]},
}


class TestUpdateMetadata:
    """Test update_metadata uses --set-metadata for waiting_for/blocked_by."""

    def test_update_metadata_waiting_for(self, storage: BeadsStorage):
        from gtdlib.metadata import GTDMetadata

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_METADATA])),  # update
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_METADATA])),  # get
            ]
            metadata = GTDMetadata(
                waiting_for={"person": "Alice", "reason": "Design mockups"}
            )
            storage.update_metadata("GTD-abc", metadata)
            cmd = mock_run.call_args_list[0][0][0]
            assert "--set-metadata" in cmd
            # Find the set-metadata argument
            idx = cmd.index("--set-metadata")
            assert "waiting_for=" in cmd[idx + 1]

    def test_update_metadata_blocked_by(self, storage: BeadsStorage):
        from gtdlib.metadata import GTDMetadata

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_BLOCKED])),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD_WITH_BLOCKED])),
            ]
            metadata = GTDMetadata(blocked_by=[42, 43])
            storage.update_metadata("GTD-abc", metadata)
            cmd = mock_run.call_args_list[0][0][0]
            assert "--set-metadata" in cmd

    def test_update_metadata_clears_waiting_for_when_none(self, storage: BeadsStorage):
        """Setting waiting_for=None must send --unset-metadata to clear the field."""
        from gtdlib.metadata import GTDMetadata

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            metadata = GTDMetadata(waiting_for=None)
            storage.update_metadata("GTD-abc", metadata)
            cmd = mock_run.call_args_list[0][0][0]
            assert "--unset-metadata" in cmd
            idx = cmd.index("--unset-metadata")
            assert cmd[idx + 1] == "waiting_for"

    def test_update_metadata_clears_due_with_empty_string(self, storage: BeadsStorage):
        """Setting due=None must send --due '' so bd clears the field."""
        from gtdlib.metadata import GTDMetadata

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            metadata = GTDMetadata(due=None)
            storage.update_metadata("GTD-abc", metadata)
            cmd = mock_run.call_args_list[0][0][0]
            assert "--due" in cmd
            assert cmd[cmd.index("--due") + 1] == ""

    def test_update_metadata_always_sends_blocked_by(self, storage: BeadsStorage):
        """Empty blocked_by [] must still be sent (not skipped) to clear the list."""
        from gtdlib.metadata import GTDMetadata

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
                _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD])),
            ]
            metadata = GTDMetadata(blocked_by=[])
            storage.update_metadata("GTD-abc", metadata)
            cmd = mock_run.call_args_list[0][0][0]
            # Must include blocked_by=[] to clear previously-set value
            assert "--set-metadata" in cmd
            meta_indices = [i for i, x in enumerate(cmd) if x == "--set-metadata"]
            meta_values = [cmd[i + 1] for i in meta_indices]
            assert any("blocked_by" in v for v in meta_values)


class TestParseMetadataFromBeadsJSON:
    """Test that bd's native metadata JSON populates GTDItem.waiting_for/blocked_by."""

    def test_parse_waiting_for_from_metadata_field(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_WITH_METADATA])
            )
            item = storage.get_item("GTD-abc")
            assert item.waiting_for is not None
            assert item.waiting_for["person"] == "Alice"

    def test_parse_blocked_by_from_metadata_field(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_BEAD_WITH_BLOCKED])
            )
            item = storage.get_item("GTD-abc")
            assert item.blocked_by == [42, 43]

    def test_no_metadata_field_means_empty(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([SAMPLE_BEAD]))
            item = storage.get_item("GTD-abc")
            assert item.waiting_for is None
            assert item.blocked_by == []


# ---------------------------------------------------------------------------
# Feature: Epics as Projects (durandom-skills-m75)
# ---------------------------------------------------------------------------

SAMPLE_EPIC = {
    "id": "GTD-epic1",
    "title": "Ship Website v2",
    "description": "Complete website relaunch",
    "status": "open",
    "priority": 1,
    "issue_type": "epic",
    "owner": "user@example.com",
    "created_at": "2026-02-01T00:00:00Z",
    "updated_at": "2026-02-01T00:00:00Z",
    "labels": [],
}

SAMPLE_EPIC_2 = {
    **SAMPLE_EPIC,
    "id": "GTD-epic2",
    "title": "Q2 Planning",
    "status": "closed",
    "closed_at": "2026-02-20T00:00:00Z",
}

SAMPLE_EPIC_STATUS = [
    {
        "id": "GTD-epic1",
        "title": "Ship Website v2",
        "children_total": 5,
        "children_closed": 3,
        "state": "open",
    }
]


class TestListMilestones:
    """Test list_milestones() returns epics as milestone dicts."""

    def test_list_open_milestones(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd list
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd show GTD-epic1
            ]
            milestones = storage.list_milestones(state="open")
            assert len(milestones) == 1
            assert milestones[0]["title"] == "Ship Website v2"
            # Verify bd list --type=epic --status=open was the first call
            cmd = mock_run.call_args_list[0][0][0]
            assert "--type" in cmd
            assert cmd[cmd.index("--type") + 1] == "epic"
            assert "--status" in cmd
            assert cmd[cmd.index("--status") + 1] == "open"

    def test_list_milestones_calls_show_per_epic(self, storage: BeadsStorage):
        """list_milestones calls bd show for each epic to fetch dependents."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd list
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd show GTD-epic1
            ]
            storage.list_milestones()
            assert mock_run.call_count == 2
            show_cmd = mock_run.call_args_list[1][0][0]
            assert show_cmd[:3] == ["bd", "show", "GTD-epic1"]

    def test_list_milestones_counts_children_from_dependents(self, storage: BeadsStorage):
        """list_milestones counts open/closed children from the dependents array."""
        epic_detailed = {
            **SAMPLE_EPIC,
            "dependents": [
                {"id": "GTD-task1", "status": "open", "dependency_type": "parent-child"},
                {"id": "GTD-task2", "status": "open", "dependency_type": "parent-child"},
                {"id": "GTD-task3", "status": "closed", "dependency_type": "parent-child"},
            ],
        }
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),       # bd list
                _mock_bd_result(stdout=_bd_json([epic_detailed])),      # bd show
            ]
            milestones = storage.list_milestones()
            assert milestones[0]["open_issues"] == 2
            assert milestones[0]["closed_issues"] == 1

    def test_list_all_milestones(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_EPIC, SAMPLE_EPIC_2])
            )
            milestones = storage.list_milestones(state="all")
            assert len(milestones) == 2

    def test_milestone_has_progress_fields(self, storage: BeadsStorage):
        """Milestone dict must have open_issues, closed_issues, state fields."""
        epic_with_children = {
            **SAMPLE_EPIC,
            "children_open": 2,
            "children_closed": 3,
        }
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([epic_with_children])
            )
            milestones = storage.list_milestones()
            m = milestones[0]
            assert "title" in m
            assert "state" in m
            assert "open_issues" in m
            assert "closed_issues" in m

    def test_closed_epic_has_state_closed(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC_2]))
            milestones = storage.list_milestones(state="closed")
            assert milestones[0]["state"] == "closed"


class TestGetMilestone:
    """Test get_milestone() finds epic by title."""

    def test_get_existing_milestone(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC]))
            m = storage.get_milestone("Ship Website v2")
            assert m is not None
            assert m["title"] == "Ship Website v2"

    def test_get_nonexistent_milestone_returns_none(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([]))
            m = storage.get_milestone("Does Not Exist")
            assert m is None

    def test_get_milestone_by_title_filters_correctly(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(
                stdout=_bd_json([SAMPLE_EPIC, SAMPLE_EPIC_2])
            )
            m = storage.get_milestone("Q2 Planning")
            assert m is not None
            assert m["title"] == "Q2 Planning"


class TestCreateMilestone:
    """Test create_milestone() creates an epic via bd create --type=epic."""

    def test_create_milestone_uses_epic_type(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([])),  # get_milestone: not found
                _mock_bd_result(stdout="GTD-epic1\n"),  # bd create --silent
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd show
            ]
            m = storage.create_milestone("Ship Website v2")
            assert m["title"] == "Ship Website v2"
            create_cmd = mock_run.call_args_list[1][0][0]  # index 1 = create call
            assert "--type" in create_cmd
            assert create_cmd[create_cmd.index("--type") + 1] == "epic"

    def test_create_milestone_with_description(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([])),  # get_milestone: not found
                _mock_bd_result(stdout="GTD-epic1\n"),  # bd create --silent
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd show
            ]
            storage.create_milestone("Ship Website v2", description="Relaunch project")
            create_cmd = mock_run.call_args_list[1][0][0]  # index 1 = create
            assert "--description" in create_cmd
            desc_idx = create_cmd.index("--description")
            assert create_cmd[desc_idx + 1] == "Relaunch project"

    def test_create_milestone_returns_existing_if_present(self, storage: BeadsStorage):
        """If epic with same title exists, return it without creating duplicate."""
        with patch("subprocess.run") as mock_run:
            # get_milestone (single call) returns existing epic
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC]))
            m = storage.create_milestone("Ship Website v2")
            assert m["title"] == "Ship Website v2"
            # Should only call bd once (get_milestone), not create
            assert mock_run.call_count == 1

    def test_create_milestone_adds_gtd_label(self, storage: BeadsStorage):
        """All epics created via GTD skill should have gtd label."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([])),  # get_milestone: not found
                _mock_bd_result(stdout="GTD-epic1\n"),  # bd create --silent
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd show
            ]
            storage.create_milestone("New Project")
            create_cmd = mock_run.call_args_list[1][0][0]  # index 1 = create call
            assert "--labels" in create_cmd
            labels_idx = create_cmd.index("--labels")
            assert create_cmd[labels_idx + 1] == "gtd"


class TestEnsureProject:
    """Test ensure_project() creates epic if not exists, returns existing otherwise."""

    def test_ensure_project_returns_existing(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC]))
            m = storage.ensure_project("Ship Website v2")
            assert m["title"] == "Ship Website v2"

    def test_ensure_project_creates_if_missing(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([])),  # get_milestone: not found
                _mock_bd_result(stdout=_bd_json([])),  # get_milestone inside create
                _mock_bd_result(stdout="GTD-new\n"),  # bd create --silent
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd show
            ]
            m = storage.ensure_project("Ship Website v2")
            assert m is not None


class TestUpdateMilestone:
    """Test update_milestone() updates epic description and/or closes it."""

    def test_update_milestone_description(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # get_milestone
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # bd update
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # re-fetch
            ]
            m = storage.update_milestone("Ship Website v2", description="New desc")
            assert m is not None
            # index 1 = update call (after initial get_milestone)
            update_cmd = mock_run.call_args_list[1][0][0]
            assert "--description" in update_cmd

    def test_update_milestone_close_state(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # get_milestone
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC_2])),  # bd close
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC_2])),  # re-fetch
            ]
            m = storage.update_milestone("Ship Website v2", state="closed")
            assert m is not None
            # index 1 = close call
            close_cmd = mock_run.call_args_list[1][0][0]
            assert "close" in close_cmd

    def test_update_nonexistent_milestone_returns_none(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([]))
            m = storage.update_milestone("Does Not Exist", description="x")
            assert m is None


class TestDeleteMilestone:
    """Test delete_milestone() closes the epic."""

    def test_delete_existing_milestone(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_bd_result(stdout=_bd_json([SAMPLE_EPIC])),  # get_milestone
                _mock_bd_result(returncode=0, stdout=""),  # bd close --force
            ]
            result = storage.delete_milestone("Ship Website v2")
            assert result is True
            close_cmd = mock_run.call_args_list[1][0][0]
            assert "close" in close_cmd
            assert "GTD-epic1" in close_cmd

    def test_delete_nonexistent_returns_false(self, storage: BeadsStorage):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = _mock_bd_result(stdout=_bd_json([]))
            result = storage.delete_milestone("Does Not Exist")
            assert result is False
