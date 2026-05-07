"""
Output Sync Service - Sync JSONL database to filesystem structure.

Manages the relationship between the JSONL database and the
meetings/ output directory structure.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from ..models import Meeting
from ..repositories import MeetingRepository

logger = logging.getLogger(__name__)


@dataclass
class SyncAction:
    """Describes a sync action to be taken."""

    action: str  # create | update | delete | skip
    meeting: Meeting
    target_path: str
    reason: str = ""


@dataclass
class ConsistencyIssue:
    """Describes a consistency issue between DB and filesystem."""

    issue_type: str  # missing_in_db | missing_in_fs | path_mismatch | data_mismatch
    path: str
    stable_id: str | None = None
    details: str = ""


@dataclass
class SyncSummary:
    """Summary of a sync operation."""

    total: int
    created: int
    updated: int
    skipped: int
    errors: list[str] = field(default_factory=list)


class OutputSyncService:
    """Service for syncing JSONL database to filesystem.

    Handles:
    - Generating filesystem structure from database
    - Verifying consistency between DB and filesystem
    - Detecting orphaned directories
    """

    def __init__(
        self,
        meeting_repo: MeetingRepository,
        output_dir: Path,
    ):
        """Initialize output sync service.

        Args:
            meeting_repo: Repository for meeting records
            output_dir: Base directory for meeting output (repo root)
        """
        self.meeting_repo = meeting_repo
        self.output_dir = Path(output_dir)
        self.meetings_dir = self.output_dir / "meetings"

    def get_sync_plan(self) -> list[SyncAction]:
        """Calculate what needs to be synced to filesystem.

        Returns:
            List of SyncActions describing what would be done
        """
        actions: list[SyncAction] = []
        synced_meetings = self.meeting_repo.get_synced()

        for meeting in synced_meetings:
            if not meeting.directory:
                actions.append(
                    SyncAction(
                        action="skip",
                        meeting=meeting,
                        target_path="",
                        reason="No directory path set",
                    )
                )
                continue

            target_path = self.output_dir / meeting.directory

            if not target_path.exists():
                actions.append(
                    SyncAction(
                        action="create",
                        meeting=meeting,
                        target_path=str(target_path),
                        reason="Directory does not exist",
                    )
                )
            else:
                # Check if metadata needs updating
                metadata_path = target_path / "metadata.json"
                if not metadata_path.exists():
                    actions.append(
                        SyncAction(
                            action="update",
                            meeting=meeting,
                            target_path=str(target_path),
                            reason="Missing metadata.json",
                        )
                    )
                else:
                    actions.append(
                        SyncAction(
                            action="skip",
                            meeting=meeting,
                            target_path=str(target_path),
                            reason="Already synced",
                        )
                    )

        return actions

    def sync_meeting(self, meeting: Meeting) -> bool:
        """Sync a single meeting's metadata to filesystem.

        Creates directory and metadata files if needed.
        Does NOT download assets (use DownloadService for that).

        Args:
            meeting: Meeting to sync

        Returns:
            True if sync successful
        """
        if not meeting.directory:
            logger.warning(f"Meeting {meeting.stable_id} has no directory path")
            return False

        target_path = self.output_dir / meeting.directory
        target_path.mkdir(parents=True, exist_ok=True)

        # Generate metadata.json
        metadata = {
            "stable_id": meeting.stable_id,
            "event_id": meeting.event_id,
            "title": meeting.title,
            "date": meeting.date,
            "time": meeting.time,
            "slug": meeting.slug,
            "tag": meeting.tag,
            "is_recurring": meeting.is_recurring,
            "is_one_on_one": meeting.is_one_on_one,
            "directory": meeting.directory,
            "status": meeting.status,
        }

        if meeting.calendar_metadata:
            metadata["calendar_metadata"] = meeting.calendar_metadata.to_dict()
        if meeting.gemini_assets:
            metadata["gemini_assets"] = meeting.gemini_assets.to_dict()

        metadata_path = target_path / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.debug(f"Synced metadata: {meeting.directory}")
        return True

    def sync_all(self, dry_run: bool = False) -> SyncSummary:
        """Sync all synced meetings to filesystem.

        Args:
            dry_run: If True, don't actually create files

        Returns:
            SyncSummary with statistics
        """
        plan = self.get_sync_plan()

        created = 0
        updated = 0
        skipped = 0
        errors: list[str] = []

        for action in plan:
            if action.action == "skip":
                skipped += 1
                continue

            if dry_run:
                logger.info(f"Would {action.action}: {action.target_path}")
                if action.action == "create":
                    created += 1
                elif action.action == "update":
                    updated += 1
                continue

            try:
                success = self.sync_meeting(action.meeting)
                if success:
                    if action.action == "create":
                        created += 1
                    elif action.action == "update":
                        updated += 1
                else:
                    errors.append(f"Failed to sync {action.meeting.stable_id}")
            except Exception as e:
                errors.append(f"Error syncing {action.meeting.stable_id}: {e}")
                logger.error(f"Sync error: {e}")

        return SyncSummary(
            total=len(plan),
            created=created,
            updated=updated,
            skipped=skipped,
            errors=errors,
        )

    def verify_consistency(self) -> list[ConsistencyIssue]:
        """Compare JSONL state with filesystem state.

        Checks for:
        - Meetings in DB without filesystem directories
        - Filesystem directories without DB records
        - Mismatched paths
        - Stale metadata

        Returns:
            List of consistency issues found
        """
        issues: list[ConsistencyIssue] = []

        # Get all synced meetings from DB
        synced_meetings = self.meeting_repo.get_synced()
        db_directories = {m.directory: m for m in synced_meetings if m.directory}

        # Scan filesystem
        fs_directories: dict[str, Path] = {}
        if self.meetings_dir.exists():
            for tag_dir in self.meetings_dir.iterdir():
                if not tag_dir.is_dir():
                    continue
                for meeting_dir in tag_dir.rglob("metadata.json"):
                    rel_path = str(meeting_dir.parent.relative_to(self.output_dir))
                    fs_directories[rel_path] = meeting_dir.parent

        # Check for meetings in DB missing from filesystem
        for directory, meeting in db_directories.items():
            if directory not in fs_directories:
                issues.append(
                    ConsistencyIssue(
                        issue_type="missing_in_fs",
                        path=directory,
                        stable_id=meeting.stable_id,
                        details=f"Meeting '{meeting.title}' not found in filesystem",
                    )
                )

        # Check for directories in filesystem missing from DB
        for directory, path in fs_directories.items():
            if directory not in db_directories:
                # Try to read metadata to get stable_id
                metadata_path = path / "metadata.json"
                stable_id = None
                if metadata_path.exists():
                    try:
                        with open(metadata_path) as f:
                            metadata = json.load(f)
                            stable_id = metadata.get("stable_id")
                    except Exception:
                        pass

                issues.append(
                    ConsistencyIssue(
                        issue_type="missing_in_db",
                        path=directory,
                        stable_id=stable_id,
                        details="Directory exists but not tracked in database",
                    )
                )

        return issues

    def find_orphaned_directories(self) -> list[Path]:
        """Find meeting directories not tracked in the database.

        Returns:
            List of orphaned directory paths
        """
        issues = self.verify_consistency()
        return [
            self.output_dir / issue.path
            for issue in issues
            if issue.issue_type == "missing_in_db"
        ]

    def import_from_filesystem(self) -> int:
        """Import meetings from existing filesystem structure into DB.

        Reads metadata.json files and creates DB records for any
        meetings not already tracked.

        Returns:
            Number of meetings imported
        """
        imported = 0

        if not self.meetings_dir.exists():
            return 0

        for metadata_path in self.meetings_dir.rglob("metadata.json"):
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)

                stable_id = metadata.get("stable_id")
                if not stable_id:
                    continue

                # Skip if already in DB
                if self.meeting_repo.exists(stable_id):
                    continue

                # Create meeting from metadata
                from ..models import CalendarMetadata, GeminiAssets

                calendar_metadata = None
                if metadata.get("calendar_metadata"):
                    calendar_metadata = CalendarMetadata.from_dict(
                        metadata["calendar_metadata"]
                    )

                gemini_assets = None
                if metadata.get("gemini_assets"):
                    gemini_assets = GeminiAssets.from_dict(metadata["gemini_assets"])

                meeting = Meeting(
                    stable_id=stable_id,
                    event_id=metadata.get("event_id", stable_id),
                    title=metadata.get("title", "Unknown"),
                    date=metadata.get("date", ""),
                    time=metadata.get("time", ""),
                    slug=metadata.get("slug"),
                    tag=metadata.get("tag"),
                    is_recurring=metadata.get("is_recurring"),
                    is_one_on_one=metadata.get("is_one_on_one", False),
                    directory=metadata.get("directory"),
                    status="synced",
                    calendar_metadata=calendar_metadata,
                    gemini_assets=gemini_assets,
                )

                self.meeting_repo.upsert(meeting)
                imported += 1
                logger.info(f"Imported: {meeting.title}")

            except Exception as e:
                logger.warning(f"Failed to import {metadata_path}: {e}")

        return imported
