"""
Meeting Repository - Query and mutate meeting records.
"""

import hashlib

from ..db import MeetingNotesDB
from ..models import Meeting


def generate_short_id(stable_id: str, length: int = 3) -> str:
    """Generate a short base36 ID from stable_id.

    Uses SHA256 hash truncated to `length` base36 characters.
    3 chars = 46,656 unique values (36^3).

    Args:
        stable_id: The full stable identifier
        length: Number of base36 characters (default 3)

    Returns:
        Short base36 string like 'a3k'
    """
    # Hash the stable_id
    hash_bytes = hashlib.sha256(stable_id.encode()).digest()

    # Convert first bytes to integer
    hash_int = int.from_bytes(hash_bytes[:4], "big")

    # Convert to base36
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = []
    for _ in range(length):
        result.append(chars[hash_int % 36])
        hash_int //= 36

    return "".join(result)


class MeetingRepository:
    """Repository for meeting records.

    Provides typed access to meetings stored in the JSONL database.
    """

    def __init__(self, db: MeetingNotesDB):
        self.db = db

    def get_by_stable_id(self, stable_id: str) -> Meeting | None:
        """Get current state of a meeting by stable_id."""
        record = self.db.get_meeting(stable_id)
        if record is None:
            return None
        return Meeting.from_dict(record.get("data", {}))

    def get_all(self) -> list[Meeting]:
        """Get all meetings."""
        records = self.db.get_all_meetings()
        return [Meeting.from_dict(r.get("data", {})) for r in records.values()]

    def get_by_status(self, status: str) -> list[Meeting]:
        """Get meetings with a specific status."""
        records = self.db.get_meetings_by_status(status)
        return [Meeting.from_dict(r.get("data", {})) for r in records]

    def get_by_date_range(self, start_date: str, end_date: str) -> list[Meeting]:
        """Get meetings within a date range (inclusive).

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        all_meetings = self.get_all()
        return [m for m in all_meetings if start_date <= m.date <= end_date]

    def get_pending_decisions(self) -> list[Meeting]:
        """Get meetings that need recurring/tag decisions.

        Returns meetings with status 'discovered' that don't have
        is_recurring and tag set.
        """
        discovered = self.get_by_status("discovered")
        return [m for m in discovered if m.is_recurring is None or m.tag is None]

    def get_ready_for_download(self) -> list[Meeting]:
        """Get meetings ready for asset download.

        Returns meetings with status 'decided'.
        """
        return self.get_by_status("decided")

    def get_synced(self) -> list[Meeting]:
        """Get meetings that have been synced to filesystem."""
        return self.get_by_status("synced")

    def exists(self, stable_id: str) -> bool:
        """Check if a meeting exists."""
        return self.db.get_meeting(stable_id) is not None

    def upsert(self, meeting: Meeting) -> str:
        """Insert or update a meeting.

        Args:
            meeting: Meeting to save

        Returns:
            Record ID
        """
        return self.db.upsert_meeting(meeting.stable_id, meeting.to_dict())

    def update_status(
        self, stable_id: str, status: str, directory: str | None = None
    ) -> None:
        """Update meeting status and optionally directory.

        Args:
            stable_id: Meeting stable_id
            status: New status
            directory: Output directory path (optional)
        """
        meeting = self.get_by_stable_id(stable_id)
        if meeting is None:
            raise ValueError(f"Meeting not found: {stable_id}")

        meeting.status = status
        if directory is not None:
            meeting.directory = directory

        self.upsert(meeting)

    def update_classification(
        self,
        stable_id: str,
        *,
        tag: str | None = None,
        is_recurring: bool | None = None,
        slug: str | None = None,
    ) -> None:
        """Update meeting classification (tag, recurring, slug).

        Args:
            stable_id: Meeting stable_id
            tag: Meeting tag (e.g., 'rhdh', 'one-on-ones')
            is_recurring: Whether meeting is recurring
            slug: Meeting slug
        """
        meeting = self.get_by_stable_id(stable_id)
        if meeting is None:
            raise ValueError(f"Meeting not found: {stable_id}")

        if tag is not None:
            meeting.tag = tag
        if is_recurring is not None:
            meeting.is_recurring = is_recurring
        if slug is not None:
            meeting.slug = slug

        # Update status to decided if classification is complete
        if meeting.tag is not None and meeting.is_recurring is not None:
            meeting.status = "decided"

        self.upsert(meeting)

    def mark_synced(self, stable_id: str, directory: str) -> None:
        """Mark meeting as synced to filesystem.

        Args:
            stable_id: Meeting stable_id
            directory: Output directory path
        """
        self.update_status(stable_id, "synced", directory)

    def delete(self, stable_id: str) -> None:
        """Delete a meeting."""
        self.db.delete_meeting(stable_id)

    def count(self) -> int:
        """Get total number of meetings."""
        return len(self.db.get_all_meetings())

    def count_by_status(self) -> dict[str, int]:
        """Get count of meetings by status."""
        all_meetings = self.get_all()
        counts: dict[str, int] = {}
        for m in all_meetings:
            counts[m.status] = counts.get(m.status, 0) + 1
        return counts

    def get_by_tag(self, tag: str) -> list[Meeting]:
        """Get meetings with a specific tag."""
        return [m for m in self.get_all() if m.tag == tag]

    def get_recurring(self, is_recurring: bool = True) -> list[Meeting]:
        """Get recurring or one-off meetings."""
        return [m for m in self.get_all() if m.is_recurring == is_recurring]

    def get_with_gemini(self, has_gemini: bool = True) -> list[Meeting]:
        """Get meetings with or without Gemini transcripts."""
        return [m for m in self.get_all() if bool(m.gemini_assets) == has_gemini]

    def get_orphaned(self) -> list[Meeting]:
        """Get orphaned meetings (Gemini emails without calendar events)."""
        return [m for m in self.get_all() if m.is_orphaned]

    def query(
        self,
        tag: str | None = None,
        is_recurring: bool | None = None,
        status: str | None = None,
        since: str | None = None,
        until: str | None = None,
        has_gemini: bool | None = None,
        is_orphaned: bool | None = None,
        is_one_on_one: bool | None = None,
    ) -> list[Meeting]:
        """Query meetings with multiple filters.

        All filters are ANDed together. Pass None to skip a filter.
        """
        meetings = self.get_all()

        if tag is not None:
            meetings = [m for m in meetings if m.tag == tag]
        if is_recurring is not None:
            meetings = [m for m in meetings if m.is_recurring == is_recurring]
        if status is not None:
            meetings = [m for m in meetings if m.status == status]
        if since is not None:
            meetings = [m for m in meetings if m.date >= since]
        if until is not None:
            meetings = [m for m in meetings if m.date <= until]
        if has_gemini is not None:
            meetings = [m for m in meetings if bool(m.gemini_assets) == has_gemini]
        if is_orphaned is not None:
            meetings = [m for m in meetings if m.is_orphaned == is_orphaned]
        if is_one_on_one is not None:
            meetings = [m for m in meetings if m.is_one_on_one == is_one_on_one]

        return meetings

    def get_all_tags(self) -> list[str]:
        """Get list of unique tags in use."""
        tags = set()
        for m in self.get_all():
            if m.tag:
                tags.add(m.tag)
        return sorted(tags)

    def build_short_id_index(self) -> dict[str, Meeting]:
        """Build a lookup index from short_id to Meeting.

        Handles collisions by appending extra characters.

        Returns:
            Dict mapping short_id to Meeting
        """
        meetings = self.get_all()
        index: dict[str, Meeting] = {}

        for m in meetings:
            short_id = generate_short_id(m.stable_id, length=3)

            # Handle collision by extending length
            if short_id in index:
                # Try 4-char, then 5-char
                for length in [4, 5, 6]:
                    short_id = generate_short_id(m.stable_id, length=length)
                    if short_id not in index:
                        break

            index[short_id] = m

        return index

    def get_by_short_id(self, short_id: str) -> Meeting | None:
        """Look up a meeting by its short ID.

        Args:
            short_id: 3+ character short ID

        Returns:
            Meeting if found, None otherwise
        """
        index = self.build_short_id_index()
        return index.get(short_id)

    def resolve_id(self, id_str: str) -> Meeting | None:
        """Resolve either a short_id or stable_id to a Meeting.

        Tries short_id first (if 3-6 chars), then stable_id.

        Args:
            id_str: Short ID or stable ID

        Returns:
            Meeting if found, None otherwise
        """
        # Try as short_id if it looks like one (3-6 lowercase alphanumeric)
        if 3 <= len(id_str) <= 6 and id_str.isalnum() and id_str.islower():
            meeting = self.get_by_short_id(id_str)
            if meeting:
                return meeting

        # Try as stable_id
        return self.get_by_stable_id(id_str)

    def get_primary(self, meeting: Meeting) -> Meeting:
        """Get the primary meeting for an alias, or the meeting itself.

        Args:
            meeting: Meeting that may be an alias

        Returns:
            Primary meeting if alias, otherwise the meeting itself
        """
        if meeting.alias_of:
            primary = self.get_by_stable_id(meeting.alias_of)
            if primary:
                return primary
        return meeting

    def get_aliases(self, stable_id: str) -> list[Meeting]:
        """Get all meetings that are aliases of the given meeting.

        Args:
            stable_id: Primary meeting's stable_id

        Returns:
            List of alias meetings
        """
        return [m for m in self.get_all() if m.alias_of == stable_id]

    def link_meetings(self, primary_id: str, alias_id: str) -> bool:
        """Link an alias meeting to a primary meeting.

        The alias will inherit the primary's tag, slug, and directory structure.

        Args:
            primary_id: stable_id of the primary meeting
            alias_id: stable_id of the meeting to become an alias

        Returns:
            True if successful
        """
        primary = self.get_by_stable_id(primary_id)
        alias = self.get_by_stable_id(alias_id)

        if not primary or not alias:
            return False

        # Prevent circular aliases
        if primary.alias_of:
            # Primary is itself an alias, use its primary instead
            primary = self.get_primary(primary)

        # Set alias relationship
        alias.alias_of = primary.stable_id

        # Inherit metadata from primary
        alias.tag = primary.tag
        alias.slug = primary.slug
        alias.is_recurring = primary.is_recurring

        self.upsert(alias)
        return True

    def unlink_meeting(self, stable_id: str) -> bool:
        """Remove alias relationship from a meeting.

        Args:
            stable_id: stable_id of the alias meeting

        Returns:
            True if successful
        """
        meeting = self.get_by_stable_id(stable_id)
        if not meeting or not meeting.alias_of:
            return False

        meeting.alias_of = None
        self.upsert(meeting)
        return True
