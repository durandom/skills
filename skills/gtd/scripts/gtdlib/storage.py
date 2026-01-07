"""Abstract storage interface for GTD items."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class GTDItem:
    """A GTD item (action, project, or goal)."""

    id: str
    title: str
    body: str | None = None
    state: str = "open"
    labels: list[str] = field(default_factory=list)
    project: str | None = None  # GTD project this item belongs to
    url: str | None = None
    created_at: str | None = None
    closed_at: str | None = None

    @property
    def context(self) -> str | None:
        """Get context label (focus/meetings/async/offsite)."""
        for label in self.labels:
            if label.startswith("context/"):
                return label.split("/")[1]
        return None

    @property
    def energy(self) -> str | None:
        """Get energy label (high/low)."""
        for label in self.labels:
            if label.startswith("energy/"):
                return label.split("/")[1]
        return None

    @property
    def status(self) -> str | None:
        """Get status label (active/waiting/someday)."""
        for label in self.labels:
            if label.startswith("status/"):
                return label.split("/")[1]
        return None

    @property
    def horizon(self) -> str | None:
        """Get horizon label (action/project/goal)."""
        for label in self.labels:
            if label.startswith("horizon/"):
                return label.split("/")[1]
        return None

    @property
    def is_inbox(self) -> bool:
        """Check if item is in inbox (unclarified).

        Inbox items have status/someday and no horizon label (not yet
        classified as action/project/goal).
        """
        has_horizon = any(label.startswith("horizon/") for label in self.labels)
        has_context = any(label.startswith("context/") for label in self.labels)
        has_energy = any(label.startswith("energy/") for label in self.labels)
        # Inbox = someday status without horizon classification or context/energy
        return not has_horizon and not has_context and not has_energy


class StorageNotSetupError(Exception):
    """Raised when storage backend is not set up."""

    pass


class GTDStorage(ABC):
    """Abstract interface for GTD storage backends."""

    # Label definitions - the canonical GTD taxonomy (12 labels)
    # See references/label-taxonomy.md for full documentation
    LABELS = {
        "context": {
            "focus": {"color": "0E8A16", "description": "Morning deep work (8am-1pm)"},
            "meetings": {
                "color": "0E8A16",
                "description": "Afternoon synchronous (2-6pm)",
            },
            "async": {"color": "0E8A16", "description": "Asynchronous communication"},
            "offsite": {
                "color": "0E8A16",
                "description": "Quarterly travel, customer visits",
            },
        },
        "energy": {
            "high": {"color": "D4C5F9", "description": "Needs context, deep thinking"},
            "low": {"color": "E4E4E4", "description": "Quick, routine, low overhead"},
        },
        "status": {
            "active": {
                "color": "D93F0B",
                "description": "Next action, ready to work on",
            },
            "waiting": {"color": "EDEDED", "description": "Blocked on someone else"},
            "someday": {"color": "C5DEF5", "description": "Not committed, maybe later"},
        },
        "horizon": {
            "action": {
                "color": "0052CC",
                "description": "Ground level: single next action",
            },
            "project": {"color": "5319E7", "description": "H1: multi-action outcome"},
            "goal": {"color": "B60205", "description": "H3: 1-2 year objective"},
        },
    }

    @classmethod
    def get_label_prefixes(cls) -> tuple[str, ...]:
        """Get GTD label prefixes (e.g., 'context/', 'energy/').

        These are the prefixes that identify GTD-managed labels.
        """
        return tuple(f"{category}/" for category in cls.LABELS.keys())

    @classmethod
    def get_all_labels(cls) -> list[str]:
        """Get flat list of all label names (e.g., 'context/focus')."""
        labels = []
        for category, items in cls.LABELS.items():
            for name in items:
                labels.append(f"{category}/{name}")
        return labels

    @classmethod
    def get_required_labels(cls) -> set[str]:
        """Get the minimum set of labels required for the system to function.

        Backends should check these exist to determine if setup is complete.
        By default, all labels are required. Override to be more lenient.
        """
        return set(cls.get_all_labels())

    @abstractmethod
    def is_setup(self) -> bool:
        """Check if the storage backend is set up and ready to use."""
        ...

    @abstractmethod
    def setup(self, verbose: bool = False, fix_drift: bool = False) -> None:
        """Set up the storage backend (create labels, etc.).

        Args:
            verbose: If True, print progress messages.
            fix_drift: If True, also fix labels with incorrect color/description.

        Raises:
            RuntimeError: If setup fails.
        """
        ...

    def ensure_setup(self) -> None:
        """Ensure storage is set up, running setup if needed.

        Raises:
            StorageNotSetupError: If setup is needed but fails.
        """
        if not self.is_setup():
            self.setup(verbose=True)

    @abstractmethod
    def create_item(
        self,
        title: str,
        labels: list[str],
        body: str | None = None,
        project: str | None = None,
    ) -> GTDItem:
        """Create a new GTD item."""
        ...

    @abstractmethod
    def get_item(self, item_id: str) -> GTDItem | None:
        """Get a single item by ID."""
        ...

    @abstractmethod
    def list_items(
        self,
        labels: list[str] | None = None,
        state: str = "open",
        project: str | None = None,
        limit: int = 100,
    ) -> list[GTDItem]:
        """List items matching criteria."""
        ...

    @abstractmethod
    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        body: str | None = None,
        labels: list[str] | None = None,
        project: str | None = None,
    ) -> GTDItem:
        """Update an existing item."""
        ...

    @abstractmethod
    def add_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Add labels to an item."""
        ...

    @abstractmethod
    def remove_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Remove labels from an item."""
        ...

    @abstractmethod
    def close_item(self, item_id: str) -> GTDItem:
        """Close/complete an item."""
        ...

    @abstractmethod
    def reopen_item(self, item_id: str) -> GTDItem:
        """Reopen a closed item."""
        ...

    @abstractmethod
    def add_comment(self, item_id: str, body: str) -> None:
        """Add a comment to an item."""
        ...

    # Convenience methods with default implementations

    def capture(self, title: str, body: str | None = None) -> GTDItem:
        """Quick capture to inbox (unclarified state)."""
        # Inbox items get status/someday only - no context, energy, or horizon
        return self.create_item(title=title, labels=["status/someday"], body=body)

    def list_inbox(self) -> list[GTDItem]:
        """List all inbox items (unclarified)."""
        # Get items with status/someday that lack horizon/context/energy
        items = self.list_items(labels=["status/someday"])
        return [item for item in items if item.is_inbox]

    def list_by_context(
        self, context: str, status: str = "active", energy: str | None = None
    ) -> list[GTDItem]:
        """List items by context."""
        labels = [f"context/{context}", f"status/{status}"]
        if energy:
            labels.append(f"energy/{energy}")
        return self.list_items(labels=labels)
