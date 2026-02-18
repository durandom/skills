"""Tests for TaskwarriorStorage backend.

Integration tests that use a real Taskwarrior installation with isolated
data directories (tmp_path). Each test gets a fresh Taskwarrior database.
"""

import shutil

import pytest
from gtdlib.backends.taskwarrior import TaskwarriorStorage

# Skip entire module if taskwarrior is not installed
pytestmark = pytest.mark.skipif(
    shutil.which("task") is None, reason="taskwarrior not installed"
)


@pytest.fixture
def storage(tmp_path):
    """Create a TaskwarriorStorage with isolated data directory."""
    data_dir = tmp_path / "taskwarrior"
    s = TaskwarriorStorage(data_dir=str(data_dir))
    s.setup()
    return s


# --- Tag Conversion (unit-level, no Taskwarrior needed) ---


class TestTagConversion:
    """Test label <-> tag conversion without touching Taskwarrior."""

    def test_label_to_tag(self):
        s = TaskwarriorStorage.__new__(TaskwarriorStorage)
        assert s._label_to_tag("context/focus") == "gtd_context_focus"

    def test_label_to_tag_energy(self):
        s = TaskwarriorStorage.__new__(TaskwarriorStorage)
        assert s._label_to_tag("energy/high") == "gtd_energy_high"

    def test_tag_to_label(self):
        s = TaskwarriorStorage.__new__(TaskwarriorStorage)
        assert s._tag_to_label("gtd_context_focus") == "context/focus"

    def test_tag_to_label_non_gtd_returns_none(self):
        s = TaskwarriorStorage.__new__(TaskwarriorStorage)
        assert s._tag_to_label("regular_tag") is None

    def test_tag_to_label_malformed_returns_none(self):
        s = TaskwarriorStorage.__new__(TaskwarriorStorage)
        assert s._tag_to_label("gtd_") is None

    def test_roundtrip_all_labels(self):
        """Every GTD label survives label -> tag -> label conversion."""
        s = TaskwarriorStorage.__new__(TaskwarriorStorage)
        from gtdlib.storage import GTDStorage

        for label in GTDStorage.get_all_labels():
            tag = s._label_to_tag(label)
            assert s._tag_to_label(tag) == label, f"Roundtrip failed for {label}"


# --- Setup ---


class TestSetup:
    """Test Taskwarrior backend initialization."""

    def test_is_setup_false_before_setup(self, tmp_path):
        s = TaskwarriorStorage(data_dir=str(tmp_path / "tw"))
        assert s.is_setup() is False

    def test_setup_creates_directory_and_taskrc(self, tmp_path):
        data_dir = tmp_path / "tw"
        s = TaskwarriorStorage(data_dir=str(data_dir))
        s.setup()
        assert data_dir.exists()
        assert (data_dir / ".taskrc").exists()

    def test_is_setup_true_after_setup(self, tmp_path):
        data_dir = tmp_path / "tw"
        s = TaskwarriorStorage(data_dir=str(data_dir))
        s.setup()
        assert s.is_setup() is True

    def test_taskrc_contains_uda_definitions(self, tmp_path):
        data_dir = tmp_path / "tw"
        s = TaskwarriorStorage(data_dir=str(data_dir))
        s.setup()
        content = (data_dir / ".taskrc").read_text()
        assert "uda.gtd_defer.type=date" in content
        assert "uda.gtd_waiting.type=string" in content

    def test_setup_idempotent(self, tmp_path):
        data_dir = tmp_path / "tw"
        s = TaskwarriorStorage(data_dir=str(data_dir))
        s.setup()
        s.setup()  # Second call should not fail
        assert s.is_setup() is True


# --- CRUD Operations ---


class TestCreateItem:
    """Test creating GTD items in Taskwarrior."""

    def test_create_simple_item(self, storage):
        item = storage.create_item(title="Buy milk", labels=["status/someday"])
        assert item.title == "Buy milk"
        assert item.id is not None
        assert item.state == "open"

    def test_create_item_with_labels(self, storage):
        item = storage.create_item(
            title="Review PR",
            labels=["context/focus", "energy/high", "status/active", "horizon/action"],
        )
        assert "context/focus" in item.labels
        assert "energy/high" in item.labels
        assert "status/active" in item.labels
        assert "horizon/action" in item.labels

    def test_create_item_with_project(self, storage):
        item = storage.create_item(
            title="Write docs", labels=["status/active"], project="website"
        )
        assert item.project == "website"

    def test_create_item_with_body(self, storage):
        item = storage.create_item(
            title="Complex task",
            labels=["status/active"],
            body="Detailed description here",
        )
        assert item.body == "Detailed description here"


class TestGetItem:
    """Test retrieving items by ID."""

    def test_get_existing_item(self, storage):
        created = storage.create_item(title="Find me", labels=["status/active"])
        fetched = storage.get_item(created.id)
        assert fetched is not None
        assert fetched.title == "Find me"
        assert fetched.id == created.id

    def test_get_nonexistent_item_returns_none(self, storage):
        result = storage.get_item("99999")
        assert result is None


class TestListItems:
    """Test listing/querying items."""

    def test_list_empty_returns_empty(self, storage):
        items = storage.list_items()
        assert items == []

    def test_list_returns_created_items(self, storage):
        storage.create_item(title="Task 1", labels=["status/active"])
        storage.create_item(title="Task 2", labels=["status/active"])
        items = storage.list_items()
        assert len(items) == 2

    def test_list_filters_by_label(self, storage):
        storage.create_item(title="Active task", labels=["status/active"])
        storage.create_item(title="Someday task", labels=["status/someday"])
        active = storage.list_items(labels=["status/active"])
        assert len(active) == 1
        assert active[0].title == "Active task"

    def test_list_filters_by_state(self, storage):
        item = storage.create_item(title="Done task", labels=["status/active"])
        storage.close_item(item.id)
        storage.create_item(title="Open task", labels=["status/active"])

        open_items = storage.list_items(state="open")
        assert len(open_items) == 1
        assert open_items[0].title == "Open task"

        closed_items = storage.list_items(state="closed")
        assert len(closed_items) == 1
        assert closed_items[0].title == "Done task"

    def test_list_filters_by_project(self, storage):
        storage.create_item(
            title="Project A task", labels=["status/active"], project="alpha"
        )
        storage.create_item(
            title="Project B task", labels=["status/active"], project="beta"
        )
        alpha = storage.list_items(project="alpha")
        assert len(alpha) == 1
        assert alpha[0].title == "Project A task"

    def test_list_respects_limit(self, storage):
        for i in range(5):
            storage.create_item(title=f"Task {i}", labels=["status/active"])
        items = storage.list_items(limit=3)
        assert len(items) == 3


class TestUpdateItem:
    """Test updating existing items."""

    def test_update_title(self, storage):
        item = storage.create_item(title="Old title", labels=["status/active"])
        updated = storage.update_item(item.id, title="New title")
        assert updated.title == "New title"

    def test_update_labels_replaces_all(self, storage):
        item = storage.create_item(
            title="Task", labels=["status/active", "context/focus"]
        )
        updated = storage.update_item(
            item.id, labels=["status/waiting", "context/meetings"]
        )
        assert "status/waiting" in updated.labels
        assert "context/meetings" in updated.labels
        assert "status/active" not in updated.labels
        assert "context/focus" not in updated.labels

    def test_update_project(self, storage):
        item = storage.create_item(title="Task", labels=["status/active"])
        updated = storage.update_item(item.id, project="new-project")
        assert updated.project == "new-project"

    def test_update_body_adds_annotation(self, storage):
        item = storage.create_item(title="Task", labels=["status/active"])
        updated = storage.update_item(item.id, body="New annotation")
        assert updated.body is not None


class TestAddRemoveLabels:
    """Test incremental label management."""

    def test_add_labels(self, storage):
        item = storage.create_item(title="Task", labels=["status/active"])
        updated = storage.add_labels(item.id, ["context/focus", "energy/high"])
        assert "context/focus" in updated.labels
        assert "energy/high" in updated.labels
        assert "status/active" in updated.labels  # Original label preserved

    def test_remove_labels(self, storage):
        item = storage.create_item(
            title="Task", labels=["status/active", "context/focus", "energy/high"]
        )
        updated = storage.remove_labels(item.id, ["context/focus"])
        assert "context/focus" not in updated.labels
        assert "status/active" in updated.labels
        assert "energy/high" in updated.labels


class TestCloseReopen:
    """Test closing and reopening items."""

    def test_close_item(self, storage):
        item = storage.create_item(title="Close me", labels=["status/active"])
        closed = storage.close_item(item.id)
        assert closed.state == "closed"

    def test_reopen_item(self, storage):
        item = storage.create_item(title="Reopen me", labels=["status/active"])
        closed = storage.close_item(item.id)
        # Must use the ID from close_item (may be UUID after completion)
        reopened = storage.reopen_item(closed.id)
        assert reopened.state == "open"

    def test_ids_stable_after_close(self, storage):
        """Closing a task must not shift IDs of other tasks.

        Reproduces the real-world bug: user sees tasks 1-5, closes #3,
        then #5 should still be #5 (not shifted to #4).
        TaskWarrior's default GC renumbers IDs — rc.gc=off prevents this.
        """
        items = []
        for i in range(1, 6):
            items.append(
                storage.create_item(title=f"Task {i}", labels=["status/active"])
            )

        # Record original IDs
        original_ids = {item.title: item.id for item in items}

        # Close task in the middle
        storage.close_item(original_ids["Task 3"])

        # Remaining open tasks must keep their original IDs
        for title in ["Task 1", "Task 2", "Task 4", "Task 5"]:
            fetched = storage.get_item(original_ids[title])
            assert fetched is not None, (
                f"{title} not found at original ID {original_ids[title]}"
            )
            assert fetched.title == title, (
                f"ID {original_ids[title]} points to '{fetched.title}'"
                f" instead of '{title}' — IDs shifted after close!"
            )


class TestAddComment:
    """Test annotations (comments)."""

    def test_add_comment(self, storage):
        item = storage.create_item(title="Task", labels=["status/active"])
        storage.add_comment(item.id, "This is a note")
        fetched = storage.get_item(item.id)
        assert fetched.body == "This is a note"


# --- Convenience Methods (from GTDStorage base class) ---


class TestCapture:
    """Test quick-capture to inbox."""

    def test_capture_creates_someday_item(self, storage):
        item = storage.capture("Quick thought")
        assert item.title == "Quick thought"
        assert "status/someday" in item.labels
        assert item.is_inbox is True

    def test_capture_with_body(self, storage):
        item = storage.capture("Idea", body="More details")
        assert item.body == "More details"


class TestListInbox:
    """Test inbox listing (unclarified items)."""

    def test_list_inbox_returns_only_unclarified(self, storage):
        storage.capture("Inbox item")
        storage.create_item(
            title="Clarified item",
            labels=["status/active", "context/focus", "energy/high", "horizon/action"],
        )
        inbox = storage.list_inbox()
        assert len(inbox) == 1
        assert inbox[0].title == "Inbox item"

    def test_list_inbox_empty_when_all_clarified(self, storage):
        storage.create_item(
            title="Clarified",
            labels=["status/someday", "horizon/project"],
        )
        inbox = storage.list_inbox()
        assert len(inbox) == 0


class TestListByContext:
    """Test context-based filtering."""

    def test_list_by_context(self, storage):
        storage.create_item(
            title="Focus task",
            labels=["status/active", "context/focus"],
        )
        storage.create_item(
            title="Meeting task",
            labels=["status/active", "context/meetings"],
        )
        focus = storage.list_by_context("focus")
        assert len(focus) == 1
        assert focus[0].title == "Focus task"

    def test_list_by_context_with_energy(self, storage):
        storage.create_item(
            title="High energy focus",
            labels=["status/active", "context/focus", "energy/high"],
        )
        storage.create_item(
            title="Low energy focus",
            labels=["status/active", "context/focus", "energy/low"],
        )
        high = storage.list_by_context("focus", energy="high")
        assert len(high) == 1
        assert high[0].title == "High energy focus"


# --- Label Introspection ---


class TestGetExistingLabels:
    """Test discovering which GTD labels are actually in use."""

    def test_empty_database_returns_empty(self, storage):
        labels = storage.get_existing_labels()
        assert labels == set()

    def test_returns_labels_from_tasks(self, storage):
        storage.create_item(title="Task", labels=["status/active", "context/focus"])
        labels = storage.get_existing_labels()
        assert "status/active" in labels
        assert "context/focus" in labels

    def test_returns_union_across_tasks(self, storage):
        storage.create_item(title="A", labels=["status/active"])
        storage.create_item(title="B", labels=["energy/high"])
        labels = storage.get_existing_labels()
        assert "status/active" in labels
        assert "energy/high" in labels

    def test_ignores_non_gtd_tags(self, storage):
        # Create item then add a non-GTD tag directly
        item = storage.create_item(title="Task", labels=["status/active"])
        storage._run_task([item.id, "modify", "+custom_tag"])
        labels = storage.get_existing_labels()
        assert "status/active" in labels
        # custom_tag should not appear (it's not a GTD label)
        assert all(
            label.startswith(("context/", "energy/", "status/", "horizon/"))
            for label in labels
        )

    def test_includes_labels_from_closed_tasks(self, storage):
        item = storage.create_item(title="Done", labels=["status/active"])
        storage.close_item(item.id)
        labels = storage.get_existing_labels()
        assert "status/active" in labels


class TestGetStaleLabels:
    """Test finding GTD-prefixed tags not in the canonical taxonomy."""

    def test_no_stale_with_valid_labels(self, storage):
        storage.create_item(title="Task", labels=["status/active"])
        stale = storage.get_stale_labels()
        assert stale == []

    def test_detects_stale_gtd_tag(self, storage):
        item = storage.create_item(title="Task", labels=["status/active"])
        # Manually add a stale GTD-prefixed tag
        storage._run_task([item.id, "modify", "+gtd_status_deprecated"])
        stale = storage.get_stale_labels()
        assert "status/deprecated" in stale

    def test_empty_database_no_stale(self, storage):
        stale = storage.get_stale_labels()
        assert stale == []


class TestGetLabelDrift:
    """Test label drift detection (TW has no label metadata)."""

    def test_returns_empty_list(self, storage):
        """TW tags have no color/description, so drift is always empty."""
        storage.create_item(title="Task", labels=["status/active"])
        drift = storage.get_label_drift()
        assert drift == []


class TestDeleteLabel:
    """Test removing a label (tag) from all tasks."""

    def test_delete_label_removes_from_all_tasks(self, storage):
        storage.create_item(title="A", labels=["status/active", "context/focus"])
        storage.create_item(title="B", labels=["status/active", "context/focus"])
        result = storage.delete_label("context/focus")
        assert result is True

        # Verify tag is gone from all tasks
        items = storage.list_items()
        for item in items:
            assert "context/focus" not in item.labels

    def test_delete_nonexistent_label_returns_false(self, storage):
        result = storage.delete_label("context/nonexistent")
        assert result is False


# --- Project / Milestone Management ---


class TestListMilestones:
    """Test listing projects as milestones."""

    def test_empty_returns_empty(self, storage):
        milestones = storage.list_milestones()
        assert milestones == []

    def test_returns_projects_with_counts(self, storage):
        storage.create_item(title="Task 1", labels=["status/active"], project="alpha")
        storage.create_item(title="Task 2", labels=["status/active"], project="alpha")
        storage.create_item(title="Task 3", labels=["status/active"], project="beta")
        milestones = storage.list_milestones()
        titles = {m["title"] for m in milestones}
        assert titles == {"alpha", "beta"}

        alpha = next(m for m in milestones if m["title"] == "alpha")
        assert alpha["open_issues"] == 2

    def test_filters_by_state(self, storage):
        item = storage.create_item(
            title="Done", labels=["status/active"], project="finished"
        )
        storage.close_item(item.id)
        storage.create_item(title="Open", labels=["status/active"], project="active")

        open_ms = storage.list_milestones(state="open")
        open_titles = {m["title"] for m in open_ms}
        # "finished" project has no open tasks left
        assert "active" in open_titles

    def test_closed_milestones(self, storage):
        """A project with only closed tasks appears in closed state."""
        item = storage.create_item(
            title="Done", labels=["status/active"], project="done-proj"
        )
        storage.close_item(item.id)

        closed_ms = storage.list_milestones(state="closed")
        closed_titles = {m["title"] for m in closed_ms}
        assert "done-proj" in closed_titles


class TestGetMilestone:
    """Test getting a single project as milestone."""

    def test_get_existing_milestone(self, storage):
        storage.create_item(title="Task", labels=["status/active"], project="myproj")
        m = storage.get_milestone("myproj")
        assert m is not None
        assert m["title"] == "myproj"
        assert m["open_issues"] == 1

    def test_get_nonexistent_returns_none(self, storage):
        m = storage.get_milestone("nonexistent")
        assert m is None

    def test_includes_closed_task_counts(self, storage):
        item = storage.create_item(
            title="Done", labels=["status/active"], project="proj"
        )
        storage.close_item(item.id)
        storage.create_item(title="Open", labels=["status/active"], project="proj")
        m = storage.get_milestone("proj")
        assert m["open_issues"] == 1
        assert m["closed_issues"] == 1


class TestCreateMilestone:
    """Test creating a project (milestone)."""

    def test_create_returns_dict(self, storage):
        m = storage.create_milestone("new-project")
        assert m["title"] == "new-project"

    def test_create_idempotent(self, storage):
        """Creating the same milestone twice returns the same data."""
        storage.create_item(title="Task", labels=["status/active"], project="existing")
        m = storage.create_milestone("existing")
        assert m["title"] == "existing"
        assert m["open_issues"] == 1


class TestEnsureProject:
    """Test ensure_project (idempotent create)."""

    def test_ensure_new_project(self, storage):
        m = storage.ensure_project("new-proj")
        assert m["title"] == "new-proj"

    def test_ensure_existing_project(self, storage):
        storage.create_item(title="Task", labels=["status/active"], project="existing")
        m = storage.ensure_project("existing")
        assert m["title"] == "existing"
        assert m["open_issues"] == 1


class TestUpdateMilestone:
    """Test updating a project (milestone)."""

    def test_update_description(self, storage):
        storage.create_item(title="Task", labels=["status/active"], project="proj")
        result = storage.update_milestone("proj", description="Updated desc")
        assert result is not None
        assert result["description"] == "Updated desc"

    def test_update_nonexistent_returns_none(self, storage):
        result = storage.update_milestone("nonexistent", description="nope")
        assert result is None

    def test_update_state_to_closed(self, storage):
        storage.create_item(title="Task", labels=["status/active"], project="proj")
        result = storage.update_milestone("proj", state="closed")
        assert result is not None
        assert result["state"] == "closed"


class TestDeleteMilestone:
    """Test deleting a project (removing project: from all tasks)."""

    def test_delete_removes_project_from_tasks(self, storage):
        storage.create_item(title="A", labels=["status/active"], project="doomed")
        storage.create_item(title="B", labels=["status/active"], project="doomed")
        result = storage.delete_milestone("doomed")
        assert result is True

        # Tasks should still exist but without the project
        items = storage.list_items()
        for item in items:
            assert item.project != "doomed"

    def test_delete_nonexistent_returns_false(self, storage):
        result = storage.delete_milestone("nonexistent")
        assert result is False

    def test_delete_preserves_other_projects(self, storage):
        storage.create_item(title="Keep", labels=["status/active"], project="keeper")
        storage.create_item(title="Remove", labels=["status/active"], project="doomed")
        storage.delete_milestone("doomed")

        items = storage.list_items()
        keeper = next(i for i in items if i.title == "Keep")
        assert keeper.project == "keeper"
