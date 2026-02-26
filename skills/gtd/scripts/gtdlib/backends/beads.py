"""Beads backend for GTD storage using bd CLI.

This backend uses the Beads/Dolt system (bd command) for GTD task storage,
enabling offline-first task management with Git-based synchronization.

Requirements:
- bd CLI installed and initialized (bd init)
- Beads database configured in current workspace

Architecture:
- GTD labels map to Beads labels (context/focus → gtd:context:focus)
- GTD metadata (due, defer, waiting) stored in Beads description
- Compatible with existing Beads workflows (email-gather, etc.)
"""

from __future__ import annotations

import json
import subprocess
from datetime import date
from typing import TYPE_CHECKING

from ..storage import GTDItem, StorageBackend, StorageNotSetupError

if TYPE_CHECKING:
    from ..config import BeadsBackendConfig


class BeadsBackend(StorageBackend):
    """Storage backend using Beads (bd CLI)."""

    def __init__(self, config: BeadsBackendConfig):
        """Initialize Beads backend with configuration."""
        self.config = config
        self._check_bd_available()

    def _check_bd_available(self) -> None:
        """Check if bd CLI is available and initialized."""
        try:
            result = subprocess.run(
                ["bd", "stats"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise StorageNotSetupError(
                    "Beads not initialized. Run 'bd init' first."
                )
        except FileNotFoundError as e:
            raise StorageNotSetupError(
                "bd command not found. Install Beads CLI first."
            ) from e

    def is_setup(self) -> bool:
        """Check if Beads backend is set up and ready."""
        try:
            self._check_bd_available()
            return True
        except StorageNotSetupError:
            return False

    def setup(self) -> None:
        """Set up Beads backend (no-op - requires manual bd init)."""
        # Beads requires manual initialization via 'bd init'
        # This is intentional to avoid accidentally creating databases
        raise StorageNotSetupError(
            "Beads must be initialized manually. Run 'bd init --prefix GTD' first."
        )

    def _run_bd(self, *args: str) -> subprocess.CompletedProcess:
        """Run bd command and return result."""
        result = subprocess.run(
            ["bd", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"bd command failed: {result.stderr}")
        return result

    def _gtd_label(self, category: str, value: str) -> str:
        """Convert GTD label to Beads label format.

        Examples:
            _gtd_label("context", "focus") -> "gtd:context:focus"
            _gtd_label("status", "active") -> "gtd:status:active"
        """
        return f"gtd:{category}:{value}"

    def _parse_gtd_labels(self, bead_labels: list[str]) -> list[str]:
        """Extract GTD labels from Beads labels.

        Args:
            bead_labels: List of Beads labels (e.g., ["gtd:context:focus", "layton"])

        Returns:
            List of GTD-style labels (e.g., ["context/focus"])
        """
        gtd_labels = []
        for label in bead_labels:
            if label.startswith("gtd:"):
                # gtd:context:focus -> context/focus
                parts = label.split(":", 2)
                if len(parts) == 3:
                    gtd_labels.append(f"{parts[1]}/{parts[2]}")
        return gtd_labels

    # TODO: Implement full StorageBackend interface
    # The following methods need implementation:

    def add_item(
        self, title: str, labels: list[str], body: str | None = None
    ) -> GTDItem:
        """Add a new GTD item to Beads.

        TODO: Implement using:
            bd create --title "..." --labels "gtd,gtd:context:focus" --description "..."
        """
        raise NotImplementedError("add_item not yet implemented for Beads backend")

    def list_items(
        self,
        state: str | None = None,
        labels: list[str] | None = None,
        project: str | None = None,
    ) -> list[GTDItem]:
        """List GTD items from Beads.

        TODO: Implement using:
            bd list --labels "gtd,..." --json
        """
        raise NotImplementedError("list_items not yet implemented for Beads backend")

    def get_item(self, item_id: str) -> GTDItem:
        """Get a single GTD item by ID.

        TODO: Implement using:
            bd show <id> --json
        """
        raise NotImplementedError("get_item not yet implemented for Beads backend")

    def update_item(
        self,
        item_id: str,
        labels_add: list[str] | None = None,
        labels_remove: list[str] | None = None,
        state: str | None = None,
        body: str | None = None,
    ) -> GTDItem:
        """Update a GTD item in Beads.

        TODO: Implement using:
            bd update <id> --add-labels "..." --remove-labels "..."
            bd comments add <id> "..." (for body updates)
        """
        raise NotImplementedError("update_item not yet implemented for Beads backend")

    def close_item(self, item_id: str) -> GTDItem:
        """Close a GTD item.

        TODO: Implement using:
            bd close <id>
        """
        raise NotImplementedError("close_item not yet implemented for Beads backend")

    def add_comment(self, item_id: str, comment: str) -> None:
        """Add a comment to a GTD item.

        TODO: Implement using:
            bd comments add <id> "..."
        """
        raise NotImplementedError("add_comment not yet implemented for Beads backend")

    def get_comments(self, item_id: str) -> list[dict]:
        """Get comments for a GTD item.

        TODO: Implement using:
            bd comments <id> --json
        """
        raise NotImplementedError("get_comments not yet implemented for Beads backend")
