"""Tests for cmd_project_show in the gtd script."""

from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Load the gtd script (no .py extension) as a module
_GTD_SCRIPT = Path(__file__).parent.parent.parent / "skills/gtd/scripts/gtd"


def _load_gtd_module():
    loader = importlib.machinery.SourceFileLoader("gtd_cmd", str(_GTD_SCRIPT))
    spec = importlib.util.spec_from_loader("gtd_cmd", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gtd_module():
    return _load_gtd_module()


def _make_args(title: str, **kwargs) -> MagicMock:
    args = MagicMock()
    args.title = title
    args.repo = None
    args.backend = "beads"
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


def _make_milestone(
    title: str,
    description: str = "",
    open_issues: int = 0,
    closed_issues: int = 0,
) -> dict:
    return {
        "id": "GTD-epic1",
        "title": title,
        "description": description,
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "state": "open",
        "due_on": None,
        "url": None,
    }


def _make_item(item_id: str, title: str, state: str = "open") -> MagicMock:
    item = MagicMock()
    item.id = item_id
    item.title = title
    item.state = state
    item.labels = []
    item.project = "Test Project"
    item.due = None
    item.defer_until = None
    return item


class TestCmdProjectShow:
    """Test cmd_project_show output."""

    def test_shows_progress_when_milestone_has_stale_zero_counts(
        self, gtd_module, capsys
    ):
        """Progress must reflect actual items, not stale milestone dict counts.

        Regression: get_milestone() returns open_issues=0 even when the epic
        has children (bd list doesn't populate dependents). The summary should
        be derived from list_items(), not from the milestone dict.
        """
        milestone = _make_milestone(
            "Test Project",
            description="My project",
            open_issues=0,  # stale — bd list never populates this
            closed_issues=0,
        )
        open_item = _make_item("GTD-task1", "Write something", state="open")
        mock_storage = MagicMock()
        mock_storage.get_milestone.return_value = milestone
        mock_storage.list_items.return_value = [open_item]

        with patch.object(gtd_module, "get_storage", return_value=mock_storage):
            result = gtd_module.cmd_project_show(_make_args("Test Project"))

        out = capsys.readouterr().out
        assert result == 0
        assert "No actions yet" not in out
        assert "0/1" in out or "Progress" in out

    def test_shows_no_actions_when_truly_empty(self, gtd_module, capsys):
        """'No actions yet' is correct when list_items returns nothing."""
        milestone = _make_milestone("Empty Project", open_issues=0, closed_issues=0)
        mock_storage = MagicMock()
        mock_storage.get_milestone.return_value = milestone
        mock_storage.list_items.return_value = []

        with patch.object(gtd_module, "get_storage", return_value=mock_storage):
            result = gtd_module.cmd_project_show(_make_args("Empty Project"))

        out = capsys.readouterr().out
        assert result == 0
        assert "No actions yet" in out

    def test_progress_counts_match_actions_list(self, gtd_module, capsys):
        """Progress numbers must match what's shown in the actions section."""
        milestone = _make_milestone("My Project", open_issues=0, closed_issues=0)
        items = [
            _make_item("GTD-1", "Open task 1", state="open"),
            _make_item("GTD-2", "Open task 2", state="open"),
            _make_item("GTD-3", "Done task", state="closed"),
        ]
        mock_storage = MagicMock()
        mock_storage.get_milestone.return_value = milestone
        mock_storage.list_items.return_value = items

        with patch.object(gtd_module, "get_storage", return_value=mock_storage):
            gtd_module.cmd_project_show(_make_args("My Project"))

        out = capsys.readouterr().out
        # 1 closed out of 3 total = 33%
        assert "1/3" in out
        assert "Open (2)" in out
        assert "Completed (1)" in out
