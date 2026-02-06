"""
JSONL Database for Meeting Notes

Append-only JSONL storage with in-memory index for fast queries.
Database stored at repository root in `.meeting-notes/` directory.
"""

import json
import logging
import os
import uuid
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# INTENT: Record types define the schema for JSONL entries
RECORD_TYPES = frozenset({"meeting", "sync_state", "pattern", "ignored", "tag"})
CURRENT_VERSION = 1


def generate_record_id(prefix: str = "rec") -> str:
    """Generate a unique record ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def find_repo_root(start_path: Path | None = None) -> Path:
    """Find repository root by looking for .git directory.

    Args:
        start_path: Starting directory (defaults to cwd)

    Returns:
        Path to repository root

    Raises:
        FileNotFoundError: If no .git directory found
    """
    path = Path(start_path or os.getcwd()).resolve()

    for parent in [path] + list(path.parents):
        if (parent / ".git").exists():
            return parent

    raise FileNotFoundError(
        f"No git repository found starting from {path}. "
        "Meeting notes database must be in a git repository."
    )


class MeetingNotesDB:
    """JSONL-based database with in-memory index.

    Database files are stored at: <repo-root>/.meeting-notes/
    - meetings.jsonl: Meeting and pattern records
    - sync.jsonl: Sync state records
    - index.json: Current state snapshot (rebuilt from JSONL)
    """

    def __init__(self, db_dir: Path | None = None):
        """Initialize database.

        Args:
            db_dir: Database directory. If None, uses <repo_root>/.meeting-notes/
        """
        if db_dir is None:
            repo_root = find_repo_root()
            db_dir = repo_root / ".meeting-notes"

        self.db_dir = Path(db_dir)
        self.meetings_file = self.db_dir / "meetings.jsonl"
        self.sync_file = self.db_dir / "sync.jsonl"
        self.index_file = self.db_dir / "index.json"

        # In-memory index: stable_id -> latest record data
        self._meetings_index: dict[str, dict[str, Any]] = {}
        self._patterns_index: dict[str, dict[str, Any]] = {}
        self._ignored_index: dict[str, dict[str, Any]] = {}
        self._tags_index: dict[str, dict[str, Any]] = {}  # name -> tag record
        self._sync_state: dict[str, Any] = {}

        self._initialized = False

    def initialize(self) -> None:
        """Create database directory and rebuild index from JSONL files."""
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # Touch files if they don't exist
        self.meetings_file.touch(exist_ok=True)
        self.sync_file.touch(exist_ok=True)

        self._rebuild_index()
        self._initialized = True
        logger.info(f"Database initialized at {self.db_dir}")

    def _ensure_initialized(self) -> None:
        """Ensure database is initialized before operations."""
        if not self._initialized:
            self.initialize()

    def _rebuild_index(self) -> None:
        """Scan JSONL files and build in-memory index.

        For each stable_id, keeps only the latest record (by timestamp).
        Handles 'delete' operations by removing from index.
        """
        self._meetings_index.clear()
        self._patterns_index.clear()
        self._ignored_index.clear()
        self._tags_index.clear()
        self._sync_state.clear()

        # Rebuild from meetings.jsonl
        for record in self._iter_jsonl(self.meetings_file):
            record_type = record.get("type")
            operation = record.get("operation", "upsert")
            stable_id = record.get("stable_id")

            if record_type == "meeting":
                if operation == "delete" and stable_id in self._meetings_index:
                    del self._meetings_index[stable_id]
                elif stable_id:
                    self._meetings_index[stable_id] = record

            elif record_type == "pattern":
                if operation == "delete" and stable_id in self._patterns_index:
                    del self._patterns_index[stable_id]
                elif stable_id:
                    self._patterns_index[stable_id] = record

            elif record_type == "ignored":
                if operation == "delete" and stable_id in self._ignored_index:
                    del self._ignored_index[stable_id]
                elif stable_id:
                    self._ignored_index[stable_id] = record

            elif record_type == "tag":
                if operation == "delete" and stable_id in self._tags_index:
                    del self._tags_index[stable_id]
                elif stable_id:
                    self._tags_index[stable_id] = record

        # Rebuild sync state from sync.jsonl (latest wins)
        for record in self._iter_jsonl(self.sync_file):
            if record.get("type") == "sync_state":
                self._sync_state = record

        # Save index snapshot for fast startup
        self._save_index()

        logger.debug(
            f"Index rebuilt: {len(self._meetings_index)} meetings, "
            f"{len(self._patterns_index)} patterns, "
            f"{len(self._ignored_index)} ignored, "
            f"{len(self._tags_index)} tags"
        )

    def _iter_jsonl(self, file_path: Path) -> Iterator[dict[str, Any]]:
        """Iterate over records in a JSONL file."""
        if not file_path.exists():
            return

        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON at {file_path}:{line_num}: {e}")

    def _append(self, file_path: Path, record: dict[str, Any]) -> None:
        """Append record to JSONL file atomically.

        Uses write-to-temp-then-append pattern for safety.
        """
        self._ensure_initialized()

        # Validate record has required fields
        if "type" not in record:
            raise ValueError("Record must have 'type' field")
        if record["type"] not in RECORD_TYPES:
            raise ValueError(f"Invalid record type: {record['type']}")

        # Add metadata if not present
        if "timestamp" not in record:
            record["timestamp"] = datetime.now().isoformat()
        if "version" not in record:
            record["version"] = CURRENT_VERSION

        # Append to file
        line = json.dumps(record, separators=(",", ":")) + "\n"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(line)

    def _save_index(self) -> None:
        """Save current index snapshot for fast startup."""
        index_data = {
            "version": CURRENT_VERSION,
            "timestamp": datetime.now().isoformat(),
            "meetings": self._meetings_index,
            "patterns": self._patterns_index,
            "ignored": self._ignored_index,
            "tags": self._tags_index,
            "sync_state": self._sync_state,
        }

        # Atomic write via temp file
        temp_file = self.index_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        temp_file.replace(self.index_file)

    # --- Meeting Operations ---

    def get_meeting(self, stable_id: str) -> dict[str, Any] | None:
        """Get current state of a meeting by stable_id."""
        self._ensure_initialized()
        return self._meetings_index.get(stable_id)

    def get_all_meetings(self) -> dict[str, dict[str, Any]]:
        """Get all meetings (stable_id -> record)."""
        self._ensure_initialized()
        return self._meetings_index.copy()

    def get_meetings_by_status(self, status: str) -> list[dict[str, Any]]:
        """Get meetings with a specific status."""
        self._ensure_initialized()
        return [
            m
            for m in self._meetings_index.values()
            if m.get("data", {}).get("status") == status
        ]

    def upsert_meeting(self, stable_id: str, data: dict[str, Any]) -> str:
        """Insert or update a meeting record.

        Args:
            stable_id: Stable meeting identifier
            data: Meeting data (title, date, slug, etc.)

        Returns:
            Record ID
        """
        self._ensure_initialized()

        record_id = generate_record_id("mtg")
        record = {
            "type": "meeting",
            "version": CURRENT_VERSION,
            "id": record_id,
            "stable_id": stable_id,
            "operation": "upsert",
            "data": data,
        }

        self._append(self.meetings_file, record)
        self._meetings_index[stable_id] = record
        self._save_index()

        return record_id

    def delete_meeting(self, stable_id: str) -> None:
        """Mark a meeting as deleted."""
        self._ensure_initialized()

        if stable_id not in self._meetings_index:
            return

        record = {
            "type": "meeting",
            "version": CURRENT_VERSION,
            "id": generate_record_id("mtg"),
            "stable_id": stable_id,
            "operation": "delete",
        }

        self._append(self.meetings_file, record)
        del self._meetings_index[stable_id]
        self._save_index()

    # --- Pattern Operations ---

    def get_pattern(self, stable_id: str) -> dict[str, Any] | None:
        """Get cached pattern for a meeting."""
        self._ensure_initialized()
        return self._patterns_index.get(stable_id)

    def get_all_patterns(self) -> dict[str, dict[str, Any]]:
        """Get all cached patterns."""
        self._ensure_initialized()
        return self._patterns_index.copy()

    def upsert_pattern(self, stable_id: str, data: dict[str, Any]) -> str:
        """Insert or update a pattern cache record."""
        self._ensure_initialized()

        record_id = generate_record_id("pat")
        record = {
            "type": "pattern",
            "version": CURRENT_VERSION,
            "id": record_id,
            "stable_id": stable_id,
            "operation": "upsert",
            "data": data,
        }

        self._append(self.meetings_file, record)
        self._patterns_index[stable_id] = record
        self._save_index()

        return record_id

    # --- Ignored Operations ---

    def get_ignored(self, stable_id: str) -> dict[str, Any] | None:
        """Check if a meeting is ignored."""
        self._ensure_initialized()
        return self._ignored_index.get(stable_id)

    def get_all_ignored(self) -> dict[str, dict[str, Any]]:
        """Get all ignored patterns."""
        self._ensure_initialized()
        return self._ignored_index.copy()

    def ignore_meeting(self, stable_id: str, reason: str) -> str:
        """Mark a meeting pattern as ignored."""
        self._ensure_initialized()

        record_id = generate_record_id("ign")
        record = {
            "type": "ignored",
            "version": CURRENT_VERSION,
            "id": record_id,
            "stable_id": stable_id,
            "operation": "upsert",
            "data": {
                "reason": reason,
                "ignored_at": datetime.now().isoformat(),
            },
        }

        self._append(self.meetings_file, record)
        self._ignored_index[stable_id] = record
        self._save_index()

        return record_id

    def unignore_meeting(self, stable_id: str) -> None:
        """Remove a meeting from ignored list."""
        self._ensure_initialized()

        if stable_id not in self._ignored_index:
            return

        record = {
            "type": "ignored",
            "version": CURRENT_VERSION,
            "id": generate_record_id("ign"),
            "stable_id": stable_id,
            "operation": "delete",
        }

        self._append(self.meetings_file, record)
        del self._ignored_index[stable_id]
        self._save_index()

    # --- Tag Operations ---

    def get_tag(self, name: str) -> dict[str, Any] | None:
        """Get tag definition by name."""
        self._ensure_initialized()
        return self._tags_index.get(name)

    def get_all_tags(self) -> dict[str, dict[str, Any]]:
        """Get all tag definitions (name -> record)."""
        self._ensure_initialized()
        return self._tags_index.copy()

    def upsert_tag(self, name: str, data: dict[str, Any]) -> str:
        """Insert or update a tag definition.

        Args:
            name: Tag name (used as stable_id)
            data: Tag data (description, color, etc.)

        Returns:
            Record ID
        """
        self._ensure_initialized()

        # Ensure name is in data
        data["name"] = name

        # Set timestamps
        now = datetime.now().isoformat()
        if name not in self._tags_index:
            data["created_at"] = now
        data["updated_at"] = now

        record_id = generate_record_id("tag")
        record = {
            "type": "tag",
            "version": CURRENT_VERSION,
            "id": record_id,
            "stable_id": name,
            "operation": "upsert",
            "data": data,
        }

        self._append(self.meetings_file, record)
        self._tags_index[name] = record
        self._save_index()

        return record_id

    def delete_tag(self, name: str) -> None:
        """Delete a tag definition."""
        self._ensure_initialized()

        if name not in self._tags_index:
            return

        record = {
            "type": "tag",
            "version": CURRENT_VERSION,
            "id": generate_record_id("tag"),
            "stable_id": name,
            "operation": "delete",
        }

        self._append(self.meetings_file, record)
        del self._tags_index[name]
        self._save_index()

    def rename_tag(self, old_name: str, new_name: str) -> str | None:
        """Rename a tag (create new, delete old).

        Args:
            old_name: Current tag name
            new_name: New tag name

        Returns:
            New record ID if successful, None if old tag not found
        """
        self._ensure_initialized()

        if old_name not in self._tags_index:
            return None

        # Get old tag data
        old_record = self._tags_index[old_name]
        old_data = old_record.get("data", {}).copy()

        # Create new tag with same data
        old_data["name"] = new_name
        record_id = self.upsert_tag(new_name, old_data)

        # Delete old tag
        self.delete_tag(old_name)

        return record_id

    # --- Sync State Operations ---

    def get_sync_state(self) -> dict[str, Any]:
        """Get current sync state."""
        self._ensure_initialized()
        return self._sync_state.get("data", {})

    def update_sync_state(self, **kwargs) -> None:
        """Update sync state fields.

        Args:
            **kwargs: Fields to update (last_calendar_check, last_email_check, etc.)
        """
        self._ensure_initialized()

        current = self._sync_state.get("data", {})
        current.update(kwargs)

        record = {
            "type": "sync_state",
            "version": CURRENT_VERSION,
            "id": generate_record_id("sync"),
            "data": current,
        }

        self._append(self.sync_file, record)
        self._sync_state = record
        self._save_index()

    # --- Utility Methods ---

    def get_stats(self) -> dict[str, int]:
        """Get database statistics."""
        self._ensure_initialized()
        return {
            "meetings": len(self._meetings_index),
            "patterns": len(self._patterns_index),
            "ignored": len(self._ignored_index),
            "tags": len(self._tags_index),
            "has_sync_state": bool(self._sync_state),
        }

    def compact(self) -> int:
        """Compact JSONL files by rewriting only current state.

        Returns:
            Number of records removed
        """
        self._ensure_initialized()

        # Count current records
        meetings_before = sum(1 for _ in self._iter_jsonl(self.meetings_file))
        sync_before = sum(1 for _ in self._iter_jsonl(self.sync_file))

        # Rewrite meetings.jsonl with only current state
        temp_file = self.meetings_file.with_suffix(".compact")
        with open(temp_file, "w", encoding="utf-8") as f:
            for record in self._meetings_index.values():
                f.write(json.dumps(record, separators=(",", ":")) + "\n")
            for record in self._patterns_index.values():
                f.write(json.dumps(record, separators=(",", ":")) + "\n")
            for record in self._ignored_index.values():
                f.write(json.dumps(record, separators=(",", ":")) + "\n")
            for record in self._tags_index.values():
                f.write(json.dumps(record, separators=(",", ":")) + "\n")
        temp_file.replace(self.meetings_file)

        # Rewrite sync.jsonl with only current state
        temp_file = self.sync_file.with_suffix(".compact")
        with open(temp_file, "w", encoding="utf-8") as f:
            if self._sync_state:
                f.write(json.dumps(self._sync_state, separators=(",", ":")) + "\n")
        temp_file.replace(self.sync_file)

        meetings_after = sum(1 for _ in self._iter_jsonl(self.meetings_file))
        sync_after = sum(1 for _ in self._iter_jsonl(self.sync_file))

        removed = (meetings_before - meetings_after) + (sync_before - sync_after)
        logger.info(f"Compacted database: removed {removed} records")

        return removed
