"""Tests for GTD history logging."""

import json
from datetime import date, datetime
from unittest.mock import patch

from gtdlib.history import HistoryEntry, format_entry_human, log_action, read_history


class TestHistoryEntry:
    """Test HistoryEntry serialization."""

    def test_to_dict_minimal(self):
        entry = HistoryEntry(ts=datetime(2026, 2, 16, 10, 0), action="capture")
        d = entry.to_dict()
        assert d["action"] == "capture"
        assert "ts" in d
        assert "item_id" not in d

    def test_to_dict_all_fields(self):
        entry = HistoryEntry(
            ts=datetime(2026, 2, 16, 10, 0),
            action="clarify",
            item_id="42",
            title="Buy milk",
            labels=["status/active"],
            review_type="daily",
            extra={"custom": "value"},
        )
        d = entry.to_dict()
        assert d["action"] == "clarify"
        assert d["item_id"] == "42"
        assert d["title"] == "Buy milk"
        assert d["labels"] == ["status/active"]
        assert d["type"] == "daily"
        assert d["custom"] == "value"

    def test_from_dict_roundtrip(self):
        original = HistoryEntry(
            ts=datetime(2026, 2, 16, 10, 0),
            action="done",
            item_id="7",
            title="Task done",
        )
        d = original.to_dict()
        restored = HistoryEntry.from_dict(d)
        assert restored.action == "done"
        assert restored.item_id == "7"
        assert restored.title == "Task done"

    def test_from_dict_missing_ts_uses_now(self):
        entry = HistoryEntry.from_dict({"action": "capture"})
        assert entry.ts is not None
        assert entry.action == "capture"

    def test_from_dict_extra_fields_preserved(self):
        entry = HistoryEntry.from_dict(
            {"ts": "2026-02-16T10:00:00", "action": "custom", "foo": "bar"}
        )
        assert entry.extra == {"foo": "bar"}


class TestLogAndRead:
    """Test log_action and read_history with tmp_path isolation."""

    def test_log_action_creates_file(self, tmp_path):
        history_path = tmp_path / ".gtd" / "history.log"
        with patch("gtdlib.history._get_history_path", return_value=history_path):
            log_action("capture", item_id="1", title="Test item")
        assert history_path.exists()

    def test_log_action_appends_jsonl(self, tmp_path):
        history_path = tmp_path / ".gtd" / "history.log"
        with patch("gtdlib.history._get_history_path", return_value=history_path):
            log_action("capture", item_id="1", title="First")
            log_action("clarify", item_id="2", title="Second")
        lines = history_path.read_text().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["action"] == "capture"
        assert json.loads(lines[1])["action"] == "clarify"

    def test_read_history_returns_most_recent_first(self, tmp_path):
        history_path = tmp_path / ".gtd" / "history.log"
        with patch("gtdlib.history._get_history_path", return_value=history_path):
            log_action("capture", title="First")
            log_action("clarify", title="Second")
            entries = read_history()
        assert entries[0].action == "clarify"
        assert entries[1].action == "capture"

    def test_read_history_respects_limit(self, tmp_path):
        history_path = tmp_path / ".gtd" / "history.log"
        with patch("gtdlib.history._get_history_path", return_value=history_path):
            for i in range(10):
                log_action("capture", title=f"Item {i}")
            entries = read_history(limit=3)
        assert len(entries) == 3

    def test_read_history_filters_by_date(self, tmp_path):
        history_path = tmp_path / ".gtd" / "history.log"
        history_path.parent.mkdir(parents=True)
        # Write entries with specific timestamps
        old = {"ts": "2025-01-01T10:00:00", "action": "old"}
        new = {"ts": "2026-02-16T10:00:00", "action": "new"}
        history_path.write_text(json.dumps(old) + "\n" + json.dumps(new) + "\n")
        with patch("gtdlib.history._get_history_path", return_value=history_path):
            entries = read_history(since=date(2026, 1, 1))
        assert len(entries) == 1
        assert entries[0].action == "new"

    def test_read_empty_history(self, tmp_path):
        history_path = tmp_path / ".gtd" / "history.log"
        with patch("gtdlib.history._get_history_path", return_value=history_path):
            entries = read_history()
        assert entries == []


class TestFormatEntry:
    """Test human-readable formatting."""

    def test_format_basic_entry(self):
        entry = HistoryEntry(ts=datetime(2026, 2, 16, 10, 30), action="capture")
        formatted = format_entry_human(entry)
        assert "2026-02-16 10:30" in formatted
        assert "capture" in formatted

    def test_format_with_title_truncation(self):
        long_title = "A" * 50
        entry = HistoryEntry(
            ts=datetime(2026, 2, 16, 10, 0), action="capture", title=long_title
        )
        formatted = format_entry_human(entry)
        assert "..." in formatted

    def test_format_with_review_type(self):
        entry = HistoryEntry(
            ts=datetime(2026, 2, 16, 10, 0), action="review", review_type="weekly"
        )
        formatted = format_entry_human(entry)
        assert "(weekly)" in formatted
