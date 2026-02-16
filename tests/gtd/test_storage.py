"""Tests for GTDItem dataclass and GTDStorage class methods."""

from gtdlib.storage import GTDItem, GTDStorage


class TestGTDItemProperties:
    """Test GTDItem convenience properties for extracting label values."""

    def test_context_extracts_value(self):
        item = GTDItem(id="1", title="t", labels=["context/focus", "status/active"])
        assert item.context == "focus"

    def test_context_returns_none_when_missing(self):
        item = GTDItem(id="1", title="t", labels=["status/active"])
        assert item.context is None

    def test_energy_extracts_value(self):
        item = GTDItem(id="1", title="t", labels=["energy/high"])
        assert item.energy == "high"

    def test_energy_returns_none_when_missing(self):
        item = GTDItem(id="1", title="t", labels=[])
        assert item.energy is None

    def test_status_extracts_value(self):
        item = GTDItem(id="1", title="t", labels=["status/waiting"])
        assert item.status == "waiting"

    def test_horizon_extracts_value(self):
        item = GTDItem(id="1", title="t", labels=["horizon/action"])
        assert item.horizon == "action"

    def test_multiple_labels_extracts_first_match(self):
        item = GTDItem(
            id="1",
            title="t",
            labels=[
                "context/focus",
                "energy/high",
                "status/active",
                "horizon/action",
            ],
        )
        assert item.context == "focus"
        assert item.energy == "high"
        assert item.status == "active"
        assert item.horizon == "action"


class TestGTDItemInbox:
    """Test inbox detection - unclarified items lack horizon/context/energy."""

    def test_item_with_only_someday_is_inbox(self):
        item = GTDItem(id="1", title="t", labels=["status/someday"])
        assert item.is_inbox is True

    def test_item_with_no_labels_is_inbox(self):
        item = GTDItem(id="1", title="t", labels=[])
        assert item.is_inbox is True

    def test_item_with_horizon_is_not_inbox(self):
        item = GTDItem(id="1", title="t", labels=["status/someday", "horizon/action"])
        assert item.is_inbox is False

    def test_item_with_context_is_not_inbox(self):
        item = GTDItem(id="1", title="t", labels=["status/someday", "context/focus"])
        assert item.is_inbox is False

    def test_item_with_energy_is_not_inbox(self):
        item = GTDItem(id="1", title="t", labels=["status/someday", "energy/high"])
        assert item.is_inbox is False

    def test_fully_clarified_item_is_not_inbox(self):
        item = GTDItem(
            id="1",
            title="t",
            labels=[
                "status/active",
                "context/focus",
                "energy/high",
                "horizon/action",
            ],
        )
        assert item.is_inbox is False


class TestGTDStorageLabels:
    """Test the class-level label taxonomy methods."""

    def test_get_all_labels_returns_12(self):
        labels = GTDStorage.get_all_labels()
        assert len(labels) == 12

    def test_get_all_labels_includes_all_categories(self):
        labels = GTDStorage.get_all_labels()
        categories = {label.split("/")[0] for label in labels}
        assert categories == {"context", "energy", "status", "horizon"}

    def test_get_all_labels_specific_values(self):
        labels = GTDStorage.get_all_labels()
        assert "context/focus" in labels
        assert "energy/high" in labels
        assert "status/active" in labels
        assert "horizon/action" in labels

    def test_get_label_prefixes(self):
        prefixes = GTDStorage.get_label_prefixes()
        assert set(prefixes) == {"context/", "energy/", "status/", "horizon/"}

    def test_get_required_labels_equals_all_labels(self):
        required = GTDStorage.get_required_labels()
        all_labels = set(GTDStorage.get_all_labels())
        assert required == all_labels
