"""Beads backend for GTD storage using bd CLI.

Uses the Beads/Dolt system (bd command) for GTD task storage,
enabling offline-first task management with Git-based synchronization.

Requirements:
- bd CLI installed and initialized (bd init)
- Beads database configured in current workspace

Architecture:
- GTD labels map to Beads labels via gtd: prefix (context/focus -> gtd:context:focus)
- Task descriptions are stored in the Beads note body
- Projects use a hybrid model: Beads epics (--type=epic) act as the project registry
  and items are associated with projects via project:<name> labels (used for filtering).
- GTD metadata (due, defer) stored as native bd fields (--due, --defer)
- GTD metadata (waiting_for, blocked_by) stored as bd --metadata JSON field
"""

from __future__ import annotations

import json
import subprocess
from datetime import date
from typing import TYPE_CHECKING

from ..metadata import GTDMetadata
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
        - due_at -> item.due (via injected _metadata)
        - defer_until -> item.defer_until (via injected _metadata)
        - metadata.waiting_for -> item.waiting_for (via injected _metadata)
        - metadata.blocked_by -> item.blocked_by (via injected _metadata)
        - created_at -> created_at
        - closed_at -> closed_at
        """
        beads_labels = data.get("labels", []) or []
        gtd_labels = self._parse_beads_labels(beads_labels)
        project = self._extract_project(beads_labels)

        # Map beads status to GTD state
        status = data.get("status", "open")
        state = "closed" if status == "closed" else "open"

        item = GTDItem(
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

        # Inject native due/defer/metadata fields directly into GTDMetadata
        # to avoid YAML parsing and enable native bd filtering
        native_metadata = self._extract_native_metadata(data)
        if not native_metadata.is_empty():
            item._metadata = native_metadata

        return item

    def _extract_native_metadata(self, data: dict) -> GTDMetadata:
        """Build GTDMetadata from bd's native due_at, defer_until, metadata fields."""
        due: date | None = None
        defer_until: date | None = None
        waiting_for: dict | None = None
        blocked_by: list[int] = []

        # Native due_at field (ISO timestamp, e.g. "2026-03-15T00:00:00Z")
        due_at = data.get("due_at")
        if due_at:
            try:
                due = date.fromisoformat(due_at[:10])  # take YYYY-MM-DD part
            except ValueError:
                pass

        # Native defer_until field
        defer_raw = data.get("defer_until")
        if defer_raw:
            try:
                defer_until = date.fromisoformat(defer_raw[:10])
            except ValueError:
                pass

        # Native metadata JSON field (dict)
        bd_metadata = data.get("metadata") or {}
        if isinstance(bd_metadata, dict):
            waiting_for = bd_metadata.get("waiting_for")
            blocked_by = bd_metadata.get("blocked_by") or []

        return GTDMetadata(
            due=due,
            defer_until=defer_until,
            waiting_for=waiting_for,
            blocked_by=blocked_by,
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
                "https://github.com/steveyegge/beads"
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
        due: str | None = None,
        defer_until: str | None = None,
    ) -> GTDItem:
        """Create a new GTD item in Beads.

        Args:
            title: Item title.
            labels: GTD labels (e.g., ["status/active", "context/focus"]).
            body: Optional description text.
            project: Optional project name (stored as project:<name> label).
            due: Optional due date (YYYY-MM-DD or relative like "+2d", "tomorrow").
            defer_until: Optional defer date (hides from ready until this date).

        Returns:
            Created GTDItem.
        """
        beads_labels = self._labels_to_beads(labels)
        if project:
            beads_labels.append(f"project:{project}")
        beads_labels.append("gtd")  # Mark as GTD-skill-managed

        args = ["create", title, "--labels", ",".join(beads_labels), "--silent"]
        if body:
            args.extend(["--description", body])
        if due:
            args.extend(["--due", due])
        if defer_until:
            args.extend(["--defer", defer_until])
        if project:
            milestone = self.ensure_project(project)
            args.extend(["--parent", milestone["id"]])

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
        overdue: bool = False,
        due_before: str | None = None,
    ) -> list[GTDItem]:
        """List items matching criteria.

        Args:
            labels: Filter by GTD labels (AND logic -- must have ALL).
            state: Filter by state: "open" or "closed".
            project: Filter by project name.
            limit: Maximum number of results.
            verbose: If True, print debug output.
            overdue: If True, filter to past-due unclosed issues (bd --overdue).
            due_before: Filter to items due before this date (YYYY-MM-DD).

        Returns:
            List of matching GTDItems.
        """
        args = ["list", "--json", "--limit", str(limit)]

        if state in ("open", "closed"):
            args.extend(["--status", state])

        if overdue:
            args.append("--overdue")
        if due_before:
            args.extend(["--due-before", due_before])

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
        due: str | None = None,
        defer_until: str | None = None,
    ) -> GTDItem:
        """Update an existing item.

        Args:
            item_id: Beads issue ID.
            title: New title (or None to keep current).
            body: New description (or None to keep current).
            labels: New complete label set (replaces all GTD labels).
            project: New project name (or None to keep current).
            due: New due date (YYYY-MM-DD or relative).
            defer_until: New defer date.

        Returns:
            Updated GTDItem.
        """
        epic_id = None
        if project:
            milestone = self.ensure_project(project)
            epic_id = milestone["id"]

        args = ["update", item_id, "--json"]

        if title is not None:
            args.extend(["--title", title])
        if body is not None:
            args.extend(["--description", body])
        if due is not None:
            args.extend(["--due", due])
        if defer_until is not None:
            args.extend(["--defer", defer_until])

        if labels is not None:
            beads_labels = self._labels_to_beads(labels)
            # When setting labels, preserve non-GTD labels and replace GTD ones
            current_beads_labels = self._get_current_beads_labels(item_id)
            # Keep only non-GTD, non-project labels from current state
            other_labels = [
                bl
                for bl in current_beads_labels
                if not bl.startswith("gtd:") and not bl.startswith("project:")
            ]
            all_beads_labels = other_labels + beads_labels
            # Add project label: new value, existing value, or nothing
            if project is not None:
                all_beads_labels.append(f"project:{project}")
            else:
                existing_project = self._extract_project(current_beads_labels)
                if existing_project:
                    all_beads_labels.append(f"project:{existing_project}")
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

        if epic_id:
            args.extend(["--parent", epic_id])

        self._run_bd(args)
        return self._get_item_or_raise(item_id)

    def update_metadata(self, item_id: str, metadata: GTDMetadata) -> GTDItem:
        """Update an item's GTD metadata using bd's native --set-metadata flag.

        Args:
            item_id: Beads issue ID.
            metadata: New metadata (waiting_for, blocked_by, due, defer_until).

        Returns:
            Updated GTDItem.
        """
        args = ["update", item_id, "--json"]

        # Always send all metadata fields so callers can clear previously-set values.
        # Use --unset-metadata to remove a key, --set-metadata to set/update it.
        if metadata.waiting_for is not None:
            args.extend(
                [
                    "--set-metadata",
                    f"waiting_for={json.dumps(metadata.waiting_for)}",
                ]
            )
        else:
            args.extend(["--unset-metadata", "waiting_for"])

        blocked_by = metadata.blocked_by or []
        args.extend(
            [
                "--set-metadata",
                f"blocked_by={json.dumps(blocked_by)}",
            ]
        )

        # Empty string clears native due/defer fields in bd.
        due_value = metadata.due.isoformat() if metadata.due is not None else ""
        args.extend(["--due", due_value])
        defer_value = (
            metadata.defer_until.isoformat() if metadata.defer_until is not None else ""
        )
        args.extend(["--defer", defer_value])

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

    # --- Epic / Project management ---
    # Epics are GTD Projects: multi-action outcomes (horizon/project in GTD terms).
    # Beads epics are returned as "milestone" dicts for compatibility with GitHub/
    # Taskwarrior backends.

    def _epic_to_milestone(self, data: dict) -> dict:
        """Convert a bd epic JSON dict to a milestone-compatible dict."""
        status = data.get("status", "open")
        state = "closed" if status == "closed" else "open"

        # Count children from dependents array when available (bd show provides this).
        # Fall back to children_open/children_closed for lightweight bd list records.
        dependents = data.get("dependents", [])
        children = [d for d in dependents if d.get("dependency_type") == "parent-child"]
        if children:
            open_count = sum(1 for c in children if c.get("status") != "closed")
            closed_count = sum(1 for c in children if c.get("status") == "closed")
        else:
            open_count = data.get("children_open", 0)
            closed_count = data.get("children_closed", 0)

        return {
            "id": data.get("id"),
            "title": data.get("title", ""),
            "description": data.get("description") or "",
            "due_on": None,
            "open_issues": open_count,
            "closed_issues": closed_count,
            "state": state,
            "url": None,
        }

    def _list_epics_raw(self, state: str = "open") -> list[dict]:
        """Query bd for epics, return raw JSON dicts.

        Args:
            state: "open", "closed", or "all" (omits --status for all).
        """
        args = ["list", "--json", "--type", "epic", "--limit", "500"]
        if state in ("open", "closed"):
            args.extend(["--status", state])
        # "all" → no --status flag, bd returns everything
        output = self._run_bd(args, check=False)
        if not output.strip():
            return []
        try:
            data = json.loads(output)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def list_milestones(self, state: str = "open") -> list[dict]:
        """List GTD projects (Beads epics) as milestone dicts.

        Args:
            state: "open", "closed", or "all".

        Returns:
            List of milestone dicts with: id, title, description, state,
            open_issues, closed_issues, due_on, url.
        """
        epics = self._list_epics_raw(state)
        result = []
        for epic in epics:
            epic_id = epic.get("id")
            try:
                raw = self._run_bd(["show", epic_id, "--json"])
                data = json.loads(raw)
                detailed = data[0] if isinstance(data, list) and data else data
                result.append(self._epic_to_milestone(detailed))
            except (RuntimeError, json.JSONDecodeError, IndexError):
                result.append(self._epic_to_milestone(epic))
        return result

    def get_milestone(self, title: str) -> dict | None:
        """Get a GTD project (Beads epic) by title.

        Uses a single bd list --type=epic call (no status filter) to find
        the epic regardless of whether it is open or closed.

        Args:
            title: Project name to find.

        Returns:
            Milestone dict or None if not found.
        """
        epics = self._list_epics_raw("all")
        for epic in epics:
            if epic.get("title") == title:
                return self._epic_to_milestone(epic)
        return None

    def create_milestone(
        self,
        title: str,
        description: str | None = None,
        due_on: str | None = None,
    ) -> dict:
        """Create a GTD project as a Beads epic.

        If an epic with the same title already exists, returns it without
        creating a duplicate.

        Args:
            title: Project name.
            description: Optional project description.
            due_on: Ignored (not yet supported in Beads epics).

        Returns:
            Milestone dict for the created (or existing) epic.
        """
        existing = self.get_milestone(title)
        if existing:
            return existing

        args = ["create", title, "--type", "epic", "--labels", "gtd", "--silent"]
        if description:
            args.extend(["--description", description])

        output = self._run_bd(args)
        epic_id = output.strip()

        try:
            raw = self._run_bd(["show", epic_id, "--json"])
            data = json.loads(raw)
            epic = data[0] if isinstance(data, list) and data else data
            return self._epic_to_milestone(epic)
        except (RuntimeError, json.JSONDecodeError, IndexError):
            return {
                "id": epic_id,
                "title": title,
                "description": description or "",
                "state": "open",
                "open_issues": 0,
                "closed_issues": 0,
                "due_on": None,
                "url": None,
            }

    def ensure_project(self, name: str) -> dict:
        """Ensure a GTD project exists as a Beads epic, creating if needed.

        Args:
            name: Project name.

        Returns:
            Milestone dict.
        """
        existing = self.get_milestone(name)
        if existing:
            return existing
        return self.create_milestone(name)

    def update_milestone(
        self,
        title: str,
        *,
        description: str | None = None,
        due_on: str | None = None,
        state: str | None = None,
    ) -> dict | None:
        """Update a GTD project (Beads epic).

        Args:
            title: Project name to find.
            description: New description (optional).
            due_on: Ignored (not yet supported).
            state: "open" or "closed" — closes/reopens the epic.

        Returns:
            Updated milestone dict, or None if not found.
        """
        milestone = self.get_milestone(title)
        if not milestone:
            return None

        epic_id = milestone["id"]

        if description is not None:
            self._run_bd(["update", epic_id, "--json", "--description", description])

        if state == "closed" and milestone["state"] != "closed":
            self._run_bd(["close", epic_id, "--json"], check=False)
        elif state == "open" and milestone["state"] == "closed":
            self._run_bd(["reopen", epic_id, "--json"], check=False)

        return self.get_milestone(title) or milestone

    def delete_milestone(self, title: str) -> bool:
        """Delete a GTD project by closing its Beads epic.

        Args:
            title: Project name to delete.

        Returns:
            True if found and closed, False if not found.
        """
        milestone = self.get_milestone(title)
        if not milestone:
            return False

        epic_id = milestone["id"]
        self._run_bd(["close", epic_id, "--force"], check=False)
        return True

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
