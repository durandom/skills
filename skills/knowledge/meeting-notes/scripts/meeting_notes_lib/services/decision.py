"""
Decision Service - Apply recurring and tag decisions to meetings.

Handles user decisions about meeting classification (recurring vs one-off,
tags for organization). Maintains the pattern cache for future auto-classification.
"""

import logging
from typing import Any

from ..models import Meeting, RecurringPattern
from ..repositories import MeetingRepository, PatternRepository
from .calendar_utils import create_directory_path

logger = logging.getLogger(__name__)


class DecisionService:
    """Service for applying meeting classification decisions.

    Handles:
    - Accepting AI suggestions
    - Applying manual overrides
    - Updating pattern cache
    - Setting directory paths
    """

    def __init__(
        self,
        meeting_repo: MeetingRepository,
        pattern_repo: PatternRepository,
    ):
        """Initialize decision service.

        Args:
            meeting_repo: Repository for meeting records
            pattern_repo: Repository for recurring patterns
        """
        self.meeting_repo = meeting_repo
        self.pattern_repo = pattern_repo

    def get_pending(self) -> list[Meeting]:
        """Get meetings that need classification decisions."""
        return self.meeting_repo.get_pending_decisions()

    def get_decision_table(self) -> list[dict[str, Any]]:
        """Get decision table for display to user.

        Returns list of dicts with meeting info and suggested classification.
        """
        pending = self.get_pending()
        table = []

        for i, meeting in enumerate(pending, 1):
            # Generate suggestion based on patterns
            suggestion = self._suggest_classification(meeting)

            table.append(
                {
                    "number": i,
                    "stable_id": meeting.stable_id,
                    "title": meeting.title,
                    "date": meeting.date,
                    "slug": meeting.slug,
                    "is_one_on_one": meeting.is_one_on_one,
                    "suggested_tag": suggestion.get("tag", "uncategorized"),
                    "suggested_recurring": suggestion.get("is_recurring", False),
                    "has_gemini_assets": meeting.gemini_assets is not None,
                }
            )

        return table

    def _suggest_classification(self, meeting: Meeting) -> dict[str, Any]:
        """Generate classification suggestion for a meeting.

        Uses heuristics to suggest tag and recurring status.
        """
        title_lower = meeting.title.lower()

        # Default suggestion
        suggestion = {
            "tag": "uncategorized",
            "is_recurring": False,
        }

        # 1:1 meetings
        if meeting.is_one_on_one:
            suggestion["tag"] = "one-on-ones"
            suggestion["is_recurring"] = True
            return suggestion

        # Keyword-based suggestions
        if any(kw in title_lower for kw in ["standup", "stand-up", "daily"]):
            suggestion["tag"] = "team"
            suggestion["is_recurring"] = True
        elif any(kw in title_lower for kw in ["weekly", "bi-weekly", "biweekly"]):
            suggestion["is_recurring"] = True
        elif any(kw in title_lower for kw in ["sync", "check-in", "checkin"]):
            suggestion["is_recurring"] = True
        elif any(kw in title_lower for kw in ["planning", "sprint", "retro"]):
            suggestion["tag"] = "planning"
            suggestion["is_recurring"] = True
        elif any(kw in title_lower for kw in ["interview", "onboarding"]):
            suggestion["tag"] = "team"
            suggestion["is_recurring"] = False
        elif any(kw in title_lower for kw in ["all-hands", "all hands", "town hall"]):
            suggestion["tag"] = "team"
            suggestion["is_recurring"] = True

        return suggestion

    def apply_decision(
        self,
        stable_id: str,
        tag: str,
        is_recurring: bool,
        slug: str | None = None,
    ) -> Meeting:
        """Apply classification decision to a single meeting.

        Args:
            stable_id: Meeting stable_id
            tag: Meeting tag (e.g., 'rhdh', 'one-on-ones', 'team')
            is_recurring: Whether meeting is recurring
            slug: Optional slug override

        Returns:
            Updated meeting

        Raises:
            ValueError: If meeting not found
        """
        meeting = self.meeting_repo.get_by_stable_id(stable_id)
        if meeting is None:
            raise ValueError(f"Meeting not found: {stable_id}")

        # Apply classification
        meeting.tag = tag
        meeting.is_recurring = is_recurring
        if slug:
            meeting.slug = slug

        # Generate directory path
        meeting.directory = create_directory_path(meeting)
        meeting.status = "decided"

        # Save meeting
        self.meeting_repo.upsert(meeting)

        # Update pattern cache
        self._update_pattern_cache(meeting)

        logger.info(
            f"Applied decision: {meeting.title} -> tag={tag}, "
            f"recurring={is_recurring}, dir={meeting.directory}"
        )

        return meeting

    def apply_decisions_batch(
        self,
        decisions: dict[str, dict[str, Any]],
    ) -> int:
        """Apply multiple classification decisions.

        Args:
            decisions: Dict mapping stable_id to decision dict with keys:
                - tag: str
                - is_recurring: bool
                - slug: Optional[str]

        Returns:
            Number of meetings updated
        """
        count = 0
        for stable_id, decision in decisions.items():
            try:
                self.apply_decision(
                    stable_id=stable_id,
                    tag=decision["tag"],
                    is_recurring=decision["is_recurring"],
                    slug=decision.get("slug"),
                )
                count += 1
            except ValueError as e:
                logger.warning(f"Failed to apply decision: {e}")
            except Exception as e:
                logger.error(f"Error applying decision for {stable_id}: {e}")

        return count

    def accept_all_suggestions(self) -> int:
        """Accept AI-suggested classifications for all pending meetings.

        Returns:
            Number of meetings updated
        """
        pending = self.get_pending()
        count = 0

        for meeting in pending:
            suggestion = self._suggest_classification(meeting)

            try:
                self.apply_decision(
                    stable_id=meeting.stable_id,
                    tag=suggestion["tag"],
                    is_recurring=suggestion["is_recurring"],
                )
                count += 1
            except Exception as e:
                logger.error(f"Error accepting suggestion for {meeting.stable_id}: {e}")

        logger.info(f"Accepted suggestions for {count} meetings")
        return count

    def accept_remaining_suggestions(self) -> int:
        """Accept suggestions only for meetings without decisions.

        Use this after applying manual overrides to fill in the rest.

        Returns:
            Number of meetings updated
        """
        # Same as accept_all_suggestions - pending meetings are those without decisions
        return self.accept_all_suggestions()

    def ignore_meeting(self, stable_id: str, reason: str = "user_ignored") -> None:
        """Mark a meeting pattern as ignored for future syncs.

        Args:
            stable_id: Meeting stable_id
            reason: Reason for ignoring
        """
        meeting = self.meeting_repo.get_by_stable_id(stable_id)
        title_pattern = meeting.title if meeting else None

        self.pattern_repo.ignore(stable_id, reason, title_pattern)

        # Delete the meeting from active list
        if meeting:
            self.meeting_repo.delete(stable_id)

        logger.info(f"Ignored meeting pattern: {stable_id}")

    def unignore_meeting(self, stable_id: str) -> None:
        """Remove a meeting from the ignored list.

        Args:
            stable_id: Meeting stable_id
        """
        self.pattern_repo.unignore(stable_id)
        logger.info(f"Unignored meeting pattern: {stable_id}")

    def _update_pattern_cache(self, meeting: Meeting) -> None:
        """Update the recurring pattern cache with meeting's classification."""
        if meeting.is_recurring is None:
            return

        existing = self.pattern_repo.get_pattern(meeting.stable_id)

        if existing:
            # Update existing pattern
            existing.tag = meeting.tag
            existing.is_recurring = meeting.is_recurring
            existing.slug = meeting.slug or existing.slug
            existing.count += 1
            existing.last_seen = meeting.date
            self.pattern_repo.upsert_pattern(existing)
        else:
            # Create new pattern
            pattern = RecurringPattern(
                stable_id=meeting.stable_id,
                slug=meeting.slug or "",
                title_pattern=meeting.title,
                is_recurring=meeting.is_recurring,
                tag=meeting.tag,
                count=1,
                first_seen=meeting.date,
                last_seen=meeting.date,
            )
            self.pattern_repo.upsert_pattern(pattern)

    def parse_inline_decisions(self, args: list[str]) -> dict[str, dict[str, Any]]:
        """Parse inline decision syntax from command line.

        Format: NUM=TAG,r|o (e.g., "1=rhdh,r" means meeting 1 -> tag=rhdh, recurring)

        Args:
            args: List of decision strings

        Returns:
            Dict mapping meeting number to decision dict
        """
        pending = self.get_pending()
        stable_id_by_number = {i: m.stable_id for i, m in enumerate(pending, 1)}

        decisions: dict[str, dict[str, Any]] = {}

        for arg in args:
            # Parse format: NUM=TAG,r|o
            match = arg.split("=")
            if len(match) != 2:
                logger.warning(f"Invalid decision format: {arg}")
                continue

            try:
                number = int(match[0])
            except ValueError:
                logger.warning(f"Invalid meeting number: {match[0]}")
                continue

            if number not in stable_id_by_number:
                logger.warning(f"Meeting number out of range: {number}")
                continue

            # Parse TAG,r|o
            parts = match[1].split(",")
            if len(parts) != 2:
                logger.warning(f"Invalid tag/recurring format: {match[1]}")
                continue

            tag = parts[0]
            is_recurring = parts[1].lower() == "r"

            stable_id = stable_id_by_number[number]
            decisions[stable_id] = {
                "tag": tag,
                "is_recurring": is_recurring,
            }

        return decisions
