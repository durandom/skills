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
            bead_with_project = {
                **SAMPLE_BEAD,
                "labels": ["gtd:status:active", "project:website"],
            }
            mock_run.side_effect = [
                _mock_bd_result(stdout="GTD-abc\n"),
                _mock_bd_result(stdout=_bd_json([bead_with_project])),
            ]
            storage.create_item(
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
            mock_run.side_effect = [
                # _get_current_beads_labels
                _mock_bd_result(stdout=_bd_json([current_bead])),
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
