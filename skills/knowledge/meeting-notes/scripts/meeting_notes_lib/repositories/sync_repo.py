"""
Sync State Repository - Manage sync timestamps and counts.
"""

from datetime import datetime

from ..db import MeetingNotesDB
from ..models import SyncState


class SyncStateRepository:
    """Repository for sync state.

    Tracks when syncs happened and processing counts.
    """

    def __init__(self, db: MeetingNotesDB):
        self.db = db

    def get_state(self) -> SyncState:
        """Get current sync state."""
        data = self.db.get_sync_state()
        if not data:
            return SyncState()
        return SyncState.from_dict(data)

    def get_last_calendar_check(self) -> str | None:
        """Get timestamp of last calendar check."""
        return self.get_state().last_calendar_check

    def get_last_email_check(self) -> str | None:
        """Get timestamp of last email check."""
        return self.get_state().last_email_check

    def get_total_processed(self) -> int:
        """Get total number of processed meetings."""
        return self.get_state().total_processed

    def update_calendar_check(
        self, timestamp: str | None = None, count: int = 0
    ) -> None:
        """Update calendar check timestamp and count.

        Args:
            timestamp: ISO format timestamp (defaults to now)
            count: Number of events processed in this sync
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        current = self.get_state()
        self.db.update_sync_state(
            last_calendar_check=timestamp,
            last_sync_count=count,
            total_processed=current.total_processed + count,
        )

    def update_email_check(self, timestamp: str | None = None) -> None:
        """Update email check timestamp.

        Args:
            timestamp: ISO format timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        self.db.update_sync_state(last_email_check=timestamp)

    def increment_processed(self, count: int = 1) -> None:
        """Increment total processed count.

        Args:
            count: Number to add to total
        """
        current = self.get_state()
        self.db.update_sync_state(total_processed=current.total_processed + count)

    def reset(self) -> None:
        """Reset sync state to initial values."""
        self.db.update_sync_state(
            last_calendar_check=None,
            last_email_check=None,
            last_sync_count=0,
            total_processed=0,
        )
