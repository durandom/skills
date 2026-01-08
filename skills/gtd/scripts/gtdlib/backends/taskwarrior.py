"""Taskwarrior backend for GTD storage.

Stores tasks in a repo-local `.gtd/taskwarrior/` directory using the `task` CLI.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from ..metadata import GTDMetadata
from ..storage import GTDItem, GTDStorage


class TaskwarriorStorage(GTDStorage):
    """GTD storage using Taskwarrior via task CLI."""

    def __init__(self, data_dir: str = ".gtd/taskwarrior"):
        """Initialize Taskwarrior storage.

        Args:
            data_dir: Directory for Taskwarrior data files (relative to repo root
                or absolute path).
        """
        self.data_dir = Path(data_dir).resolve()
        self._env = self._build_env()

    def _build_env(self) -> dict[str, str]:
        """Build environment with TASKDATA and TASKRC pointing to local dir."""
        env = os.environ.copy()
        env["TASKDATA"] = str(self.data_dir)
        env["TASKRC"] = str(self.data_dir / ".taskrc")
        return env

    def _run_task(
        self, args: list[str], check: bool = True, verbose: bool = False
    ) -> str:
        """Run a task command and return output.

        Args:
            args: Command arguments to pass to task.
            check: If True, raise on non-zero exit code.
            verbose: If True, print debug output.

        Returns:
            stdout from the command.

        Raises:
            RuntimeError: If check=True and command fails.
        """
        # Disable confirmation prompts; use minimal verbosity but keep 'new' for add
        # 'new' shows "Created task N." which we need to parse
        cmd = ["task", "rc.confirmation=off", "rc.verbose=new"] + args
        if verbose:
            print(f"  [DEBUG] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, env=self._env)
        if result.returncode != 0:
            if check:
                raise RuntimeError(f"task command failed: {result.stderr}")
            return ""
        return result.stdout

    # --- Label/Tag Conversion ---

    def _label_to_tag(self, label: str) -> str:
        """Convert GTD label to Taskwarrior tag.

        Example: context/focus -> gtd_context_focus
        """
        return "gtd_" + label.replace("/", "_")

    def _tag_to_label(self, tag: str) -> str | None:
        """Convert Taskwarrior tag to GTD label.

        Example: gtd_context_focus -> context/focus
        Returns None if tag is not a GTD tag.
        """
        if not tag.startswith("gtd_"):
            return None
        # gtd_context_focus -> context_focus -> context/focus
        rest = tag[4:]  # Remove 'gtd_' prefix
        parts = rest.split("_", 1)
        if len(parts) == 2:
            return f"{parts[0]}/{parts[1]}"
        return None

    # --- GTDStorage Implementation ---

    def is_setup(self) -> bool:
        """Check if Taskwarrior data directory and config exist."""
        taskrc = self.data_dir / ".taskrc"
        return self.data_dir.exists() and taskrc.exists()

    def setup(self, verbose: bool = False, fix_drift: bool = False) -> None:
        """Initialize Taskwarrior data directory and config.

        Creates the data directory and .taskrc with UDA definitions for
        GTD-specific metadata fields.
        """
        self.data_dir.mkdir(parents=True, exist_ok=True)

        taskrc = self.data_dir / ".taskrc"
        if not taskrc.exists() or fix_drift:
            config_lines = [
                "# GTD Taskwarrior Configuration",
                "# Auto-generated - modifications may be overwritten",
                "",
                f"data.location={self.data_dir}",
                "",
                "# UDAs for GTD metadata",
                "uda.gtd_defer.type=date",
                "uda.gtd_defer.label=Defer Until",
                "",
                "uda.gtd_waiting.type=string",
                "uda.gtd_waiting.label=Waiting For",
                "",
                "# Disable color for clean output parsing",
                "color=off",
                "",
                "# Include completed tasks in export by default",
                "report.export.filter=",
            ]
            taskrc.write_text("\n".join(config_lines) + "\n")
            if verbose:
                print(f"✓ Created {taskrc}")

        if verbose:
            print(f"✓ Taskwarrior data directory: {self.data_dir}")

    def _parse_task(self, data: dict) -> GTDItem:
        """Parse task export JSON into GTDItem."""
        # Extract GTD labels from tags
        labels = []
        for tag in data.get("tags", []):
            label = self._tag_to_label(tag)
            if label:
                labels.append(label)

        # Map Taskwarrior status to GTD state
        tw_status = data.get("status", "pending")
        state = "closed" if tw_status in ("completed", "deleted") else "open"

        # Get first annotation as body (if any)
        annotations = data.get("annotations", [])
        first_annotation = annotations[0] if annotations else None
        body = (
            first_annotation.get("description")
            if isinstance(first_annotation, dict)
            else None
        )

        # Build metadata from Taskwarrior fields
        # Note: Metadata is reconstructed from TW attributes, not stored in body
        # The GTDItem.metadata property will use this body, but we store
        # TW-native fields directly

        return GTDItem(
            id=str(data.get("id", data.get("uuid", ""))),
            title=data.get("description", ""),
            body=body,
            state=state,
            labels=labels,
            project=data.get("project"),
            url=None,  # Taskwarrior has no URL concept
            created_at=data.get("entry"),
            closed_at=data.get("end"),
        )

    def create_item(
        self,
        title: str,
        labels: list[str],
        body: str | None = None,
        project: str | None = None,
    ) -> GTDItem:
        """Create a new task."""
        args = ["add", title]

        # Add tags for labels
        for label in labels:
            args.append(f"+{self._label_to_tag(label)}")

        # Add project if specified
        if project:
            args.append(f"project:{project}")

        output = self._run_task(args)

        # Extract task ID from output: "Created task 42."
        match = re.search(r"Created task (\d+)", output)
        if not match:
            raise RuntimeError(f"Failed to parse task ID from: {output}")

        task_id = match.group(1)

        # Add body as annotation if provided
        if body:
            self._run_task([task_id, "annotate", body])

        item = self.get_item(task_id)
        if item is None:
            raise RuntimeError(f"Task {task_id} not found after creation")
        return item

    def get_item(self, item_id: str) -> GTDItem | None:
        """Get a single task by ID."""
        try:
            # Export specific task by ID (syntax: task <id> export)
            output = self._run_task([item_id, "export"])
            if not output.strip():
                return None
            data = json.loads(output)
            if isinstance(data, list):
                if not data:
                    return None
                return self._parse_task(data[0])
            return self._parse_task(data)
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
        """List tasks matching criteria."""
        args = []

        # Status filter
        if state == "open":
            args.append("status:pending")
        elif state == "closed":
            args.append("status:completed")
        # state="all" means no status filter

        # Label/tag filters
        if labels:
            for label in labels:
                args.append(f"+{self._label_to_tag(label)}")

        # Project filter
        if project:
            args.append(f"project:{project}")

        # Add export command at end
        args.append("export")

        output = self._run_task(args, verbose=verbose, check=False)
        if not output.strip():
            return []

        try:
            data = json.loads(output)
            items = [self._parse_task(task) for task in data[:limit]]
            if verbose:
                print(f"  [DEBUG] Got {len(items)} items from Taskwarrior")
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
        """Update an existing task."""
        args = [item_id, "modify"]

        if title:
            args.append(f"description:{title}")

        if project is not None:
            if project:
                args.append(f"project:{project}")
            else:
                args.append("project:")  # Clear project

        if labels is not None:
            # Remove all existing GTD tags first (batched in a single modify command)
            current = self.get_item(item_id)
            if current:
                for label in current.labels:
                    args.append(f"-{self._label_to_tag(label)}")
            # Add new tags
            for label in labels:
                args.append(f"+{self._label_to_tag(label)}")

        # Run modify if there are changes beyond just [item_id, "modify"]
        # This handles labels=[] case where we only remove tags
        if len(args) > 2:
            self._run_task(args)

        # Handle body update via annotation
        if body is not None:
            # Taskwarrior annotations are append-only
            # Add new annotation with the body content
            self._run_task([item_id, "annotate", body])

        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"Task {item_id!r} not found after update")
        return item

    def add_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Add tags to a task."""
        args = [item_id, "modify"]
        for label in labels:
            args.append(f"+{self._label_to_tag(label)}")
        self._run_task(args)
        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"Task {item_id!r} not found after adding labels")
        return item

    def remove_labels(self, item_id: str, labels: list[str]) -> GTDItem:
        """Remove tags from a task."""
        args = [item_id, "modify"]
        for label in labels:
            args.append(f"-{self._label_to_tag(label)}")
        self._run_task(args, check=False)  # May fail if tag doesn't exist
        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"Task {item_id!r} not found after removing labels")
        return item

    def close_item(self, item_id: str) -> GTDItem:
        """Mark task as done."""
        self._run_task([item_id, "done"])
        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"Task {item_id!r} not found after closing")
        return item

    def reopen_item(self, item_id: str) -> GTDItem:
        """Reopen a completed task."""
        # Taskwarrior requires modify to change status back to pending
        self._run_task([item_id, "modify", "status:pending"])
        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"Task {item_id!r} not found after reopening")
        return item

    def add_comment(self, item_id: str, body: str) -> None:
        """Add an annotation to a task."""
        self._run_task([item_id, "annotate", body])

    # --- Metadata Management ---

    def update_metadata(self, item_id: str, metadata: GTDMetadata) -> GTDItem:
        """Update task with GTD metadata using Taskwarrior attributes.

        Maps GTD metadata to Taskwarrior native and UDA fields:
        - due -> native due: attribute
        - defer_until -> gtd_defer UDA
        - waiting_for -> gtd_waiting UDA (JSON string)
        - blocked_by -> native depends: (requires UUID resolution)
        """
        args = [item_id, "modify"]

        # Due date (native)
        if metadata.due:
            args.append(f"due:{metadata.due.isoformat()}")
        else:
            args.append("due:")  # Clear

        # Defer until (UDA)
        if metadata.defer_until:
            args.append(f"gtd_defer:{metadata.defer_until.isoformat()}")
        else:
            args.append("gtd_defer:")

        # Waiting for (UDA, JSON string)
        if metadata.waiting_for:
            args.append(f"gtd_waiting:{json.dumps(metadata.waiting_for)}")
        else:
            args.append("gtd_waiting:")

        # Blocked by (native depends)
        if metadata.blocked_by:
            uuids = self._ids_to_uuids(metadata.blocked_by)
            if uuids:
                args.append(f"depends:{','.join(uuids)}")
        else:
            args.append("depends:")

        self._run_task(args)
        item = self.get_item(item_id)
        if item is None:
            raise ValueError(f"Task {item_id!r} not found after metadata update")
        return item

    def _ids_to_uuids(self, ids: list[int]) -> list[str]:
        """Convert task IDs to UUIDs for depends attribute."""
        uuids = []
        for task_id in ids:
            try:
                output = self._run_task([str(task_id), "export"])
                data = json.loads(output)
                if isinstance(data, list) and data:
                    uuid = data[0].get("uuid", "")
                    if uuid:
                        uuids.append(uuid)
            except (RuntimeError, json.JSONDecodeError):
                # Skip invalid or non-existent task IDs silently
                pass
        return uuids

    def _resolve_depends(self, depends: str) -> list[int]:
        """Convert depends UUIDs to task IDs."""
        if not depends:
            return []
        uuids = depends.split(",")
        ids = []
        for uuid in uuids:
            try:
                output = self._run_task([uuid.strip(), "export"])
                data = json.loads(output)
                if isinstance(data, list) and data:
                    task_id = data[0].get("id")
                    if task_id:
                        ids.append(int(task_id))
            except (RuntimeError, json.JSONDecodeError, ValueError):
                # Skip invalid or non-existent UUIDs silently
                pass
        return ids
