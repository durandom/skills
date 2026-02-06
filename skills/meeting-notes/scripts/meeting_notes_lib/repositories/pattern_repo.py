"""
Pattern Repository - Query and mutate recurring pattern records.
"""

from ..db import MeetingNotesDB
from ..models import IgnoredPattern, RecurringPattern


class PatternRepository:
    """Repository for recurring pattern cache.

    Patterns store user decisions about how to classify meetings
    with similar titles. This enables automatic classification
    of future instances of recurring meetings.
    """

    def __init__(self, db: MeetingNotesDB):
        self.db = db

    # --- Recurring Patterns ---

    def get_pattern(self, stable_id: str) -> RecurringPattern | None:
        """Get cached pattern for a meeting."""
        record = self.db.get_pattern(stable_id)
        if record is None:
            return None
        return RecurringPattern.from_dict(record.get("data", {}))

    def get_all_patterns(self) -> list[RecurringPattern]:
        """Get all cached patterns."""
        records = self.db.get_all_patterns()
        return [RecurringPattern.from_dict(r.get("data", {})) for r in records.values()]

    def get_patterns_dict(self) -> dict[str, RecurringPattern]:
        """Get patterns as dict keyed by stable_id."""
        return {p.stable_id: p for p in self.get_all_patterns()}

    def upsert_pattern(self, pattern: RecurringPattern) -> str:
        """Insert or update a pattern.

        Args:
            pattern: Pattern to save

        Returns:
            Record ID
        """
        return self.db.upsert_pattern(pattern.stable_id, pattern.to_dict())

    def find_matching_pattern(self, stable_id: str) -> RecurringPattern | None:
        """Find a pattern that matches the given stable_id.

        This is useful for auto-applying cached decisions to new
        instances of recurring meetings.
        """
        return self.get_pattern(stable_id)

    def update_pattern_count(self, stable_id: str, date: str) -> None:
        """Increment pattern count and update last_seen date.

        Args:
            stable_id: Pattern stable_id
            date: Meeting date (YYYY-MM-DD)
        """
        pattern = self.get_pattern(stable_id)
        if pattern is None:
            return

        pattern.count += 1
        pattern.last_seen = date
        self.upsert_pattern(pattern)

    # --- Ignored Patterns ---

    def get_ignored(self, stable_id: str) -> IgnoredPattern | None:
        """Check if a meeting pattern is ignored."""
        record = self.db.get_ignored(stable_id)
        if record is None:
            return None
        data = record.get("data", {})
        data["stable_id"] = stable_id
        return IgnoredPattern.from_dict(data)

    def get_all_ignored(self) -> list[IgnoredPattern]:
        """Get all ignored patterns."""
        records = self.db.get_all_ignored()
        result = []
        for stable_id, record in records.items():
            data = record.get("data", {})
            data["stable_id"] = stable_id
            result.append(IgnoredPattern.from_dict(data))
        return result

    def is_ignored(self, stable_id: str) -> bool:
        """Check if a stable_id is in the ignored list."""
        return self.db.get_ignored(stable_id) is not None

    def ignore(
        self,
        stable_id: str,
        reason: str = "user_ignored",
        title_pattern: str | None = None,
    ) -> str:
        """Add a meeting pattern to the ignored list.

        Args:
            stable_id: Meeting stable_id
            reason: Reason for ignoring
            title_pattern: Optional title pattern for display

        Returns:
            Record ID
        """
        return self.db.ignore_meeting(stable_id, reason)

    def unignore(self, stable_id: str) -> None:
        """Remove a meeting pattern from the ignored list."""
        self.db.unignore_meeting(stable_id)

    # --- Statistics ---

    def count_patterns(self) -> int:
        """Get total number of cached patterns."""
        return len(self.db.get_all_patterns())

    def count_ignored(self) -> int:
        """Get total number of ignored patterns."""
        return len(self.db.get_all_ignored())
