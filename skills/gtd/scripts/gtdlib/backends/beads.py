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

    def _get_item_or_raise(self, item_id: str) -> GTDItem:
        """Get item by ID, raising if not found (for post-mutation fetches)."""
        item = self.get_item(item_id)
        if item is None:
            raise RuntimeError(f"Item {item_id} not found after mutation")
        return item

    # --- GTDStorage Implementation ---

    def is_setup(self) -> bool:
        """Check if bd CLI is available and a Beads database exists."""
        try:
            self._run_bd(["status", "--json"], check=True)
            return True
        except (RuntimeError, FileNotFoundError):
            return False

    def setup(self, verbose: bool = False, fix_drift: bool = False) -> None:  # noqa: ARG002
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
                f"Beads database not initialized. Run 'bd init' first. Error: {e}"
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

        return self._get_item_or_raise(item_id)

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
            # When setting labels, preserve non-GTD labels and replace GTD ones
            current_beads_labels = self._get_current_beads_labels(item_id)
            non_gtd_labels = [
                bl for bl in current_beads_labels if not bl.startswith("gtd:")
            ]
            # Handle project labels
            if project is not None:
                non_gtd_labels = [
                    bl for bl in non_gtd_labels if not bl.startswith("project:")
                ]
            all_beads_labels = non_gtd_labels + beads_labels
            if project is not None:
                all_beads_labels.append(f"project:{project}")
            elif any(bl.startswith("project:") for bl in current_beads_labels):
                # Preserve existing project label
                for bl in current_beads_labels:
                    if bl.startswith("project:"):
                        all_beads_labels.append(bl)
                        break
            args.extend(["--set-labels", ",".join(all_beads_labels)])
        elif project is not None:
            # Only updating project, not labels
            current_beads_labels = self._get_current_beads_labels(item_id)
            updated_labels = [
                bl for bl in current_beads_labels if not bl.startswith("project:")
            ]
            if project:
                updated_labels.append(f"project:{project}")
            args.extend(["--set-labels", ",".join(updated_labels)])

        self._run_bd(args)
        return self._get_item_or_raise(item_id)

    def _get_current_beads_labels(self, item_id: str) -> list[str]:
        """Get current raw Beads labels for an item."""
        try:
            output = self._run_bd(["show", item_id, "--json"], check=False)
            data = json.loads(output)
            if isinstance(data, list) and data:
                return data[0].get("labels", []) or []
            return []
        except (json.JSONDecodeError, RuntimeError):
            return []

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
        return self._get_item_or_raise(item_id)

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
        return self._get_item_or_raise(item_id)

    def close_item(self, item_id: str) -> GTDItem:
        """Close/complete an item.

        Args:
            item_id: Beads issue ID.

        Returns:
            Updated GTDItem with state="closed".
        """
        self._run_bd(["close", item_id, "--json"])
        return self._get_item_or_raise(item_id)

    def reopen_item(self, item_id: str) -> GTDItem:
        """Reopen a closed item.

        Args:
            item_id: Beads issue ID.

        Returns:
            Updated GTDItem with state="open".
        """
        self._run_bd(["reopen", item_id, "--json"])
        return self._get_item_or_raise(item_id)

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
                label_str = (
                    beads_label
                    if isinstance(beads_label, str)
                    else beads_label.get("name", "")
                )
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
