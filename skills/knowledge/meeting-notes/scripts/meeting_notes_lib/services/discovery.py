"""
Discovery Service - Calendar and email discovery with bidirectional matching.

Replaces the duplicated logic in CalendarDiscovery, EmailMatching, and MeetingSync
with a single unified service.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any

from ..models import GeminiAsset, GeminiAssets, Meeting
from ..repositories import MeetingRepository, PatternRepository, SyncStateRepository
from .calendar_utils import (
    create_directory_path,
    create_meeting_from_gemini_email,
    extract_meeting_metadata,
    generate_slug,
    should_include_event,
)

logger = logging.getLogger(__name__)


class DiscoveryService:
    """Unified calendar and email discovery service.

    Performs bidirectional discovery:
    1. Calendar events -> match with Gemini emails
    2. Orphaned Gemini emails -> create meetings without calendar events

    Replaces CalendarDiscovery + EmailMatching + MeetingSync classes.
    """

    def __init__(
        self,
        gwt,  # GWTInvoker - not typed to avoid circular import
        meeting_repo: MeetingRepository,
        pattern_repo: PatternRepository,
        sync_repo: SyncStateRepository,
        config: dict[str, Any],
    ):
        """Initialize discovery service.

        Args:
            gwt: GWTInvoker instance for API calls
            meeting_repo: Repository for meeting records
            pattern_repo: Repository for recurring patterns
            sync_repo: Repository for sync state
            config: Configuration dict with user_email, calendar_id, etc.
        """
        self.gwt = gwt
        self.meeting_repo = meeting_repo
        self.pattern_repo = pattern_repo
        self.sync_repo = sync_repo
        self.config = config

    def sync(
        self,
        after_date: str | None = None,
        before_date: str | None = None,
        force: bool = False,
    ) -> list[Meeting]:
        """Execute combined calendar + email discovery.

        Args:
            after_date: Start date (YYYY-MM-DD). Defaults to last sync or 7 days ago.
            before_date: End date (YYYY-MM-DD). Defaults to today.
            force: If True, re-process already processed events.

        Returns:
            List of discovered/updated meetings
        """
        logger.info("Starting meeting discovery sync")

        # Determine date range
        if after_date is None:
            last_check = self.sync_repo.get_last_calendar_check()
            if last_check:
                after_date = last_check[:10]  # Extract YYYY-MM-DD
            else:
                # Default: 7 days ago
                after_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        if before_date is None:
            before_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Date range: {after_date} to {before_date}")

        # Get sets for filtering
        processed_events: set[str] = set()
        ignored_stable_ids: set[str] = set()

        if not force:
            # Get already synced meetings
            synced = self.meeting_repo.get_synced()
            processed_events = {m.event_id for m in synced}

            # Get ignored patterns
            ignored = self.pattern_repo.get_all_ignored()
            ignored_stable_ids = {p.stable_id for p in ignored}

        # Step 1: Fetch calendar events
        logger.info("Fetching calendar events...")
        calendar_events = self._fetch_calendar_events(after_date, before_date)
        logger.info(f"Found {len(calendar_events)} calendar events")

        # Step 2: Filter and extract meetings
        meetings: list[Meeting] = []
        for event in calendar_events:
            if not should_include_event(event, processed_events, ignored_stable_ids):
                continue

            meeting = extract_meeting_metadata(event)
            meetings.append(meeting)

        logger.info(f"After filtering: {len(meetings)} meetings to process")

        # Step 3: Search for Gemini emails and match
        logger.info("Searching for Gemini emails...")
        matched_email_ids: set[str] = set()

        for meeting in meetings:
            gemini_assets = self._find_gemini_assets(meeting)
            if gemini_assets:
                meeting.gemini_assets = gemini_assets
                # Track matched email IDs
                if gemini_assets.transcript:
                    matched_email_ids.add(gemini_assets.transcript.email_id or "")
                if gemini_assets.summary:
                    matched_email_ids.add(gemini_assets.summary.email_id or "")

        # Step 4: Find orphaned Gemini emails (no calendar match)
        logger.info("Checking for orphaned Gemini emails...")
        orphaned = self._find_orphaned_gemini_emails(
            after_date, before_date, matched_email_ids
        )
        logger.info(f"Found {len(orphaned)} orphaned Gemini emails")
        meetings.extend(orphaned)

        # Step 5: Apply cached patterns and generate slugs
        logger.info("Applying patterns and generating slugs...")
        for meeting in meetings:
            self._apply_pattern_or_generate_slug(meeting)

        # Step 6: Persist meetings to database
        logger.info("Persisting meetings to database...")
        for meeting in meetings:
            existing = self.meeting_repo.get_by_stable_id(meeting.stable_id)
            if existing is None:
                self.meeting_repo.upsert(meeting)
            else:
                # Update existing meeting with new data
                existing.gemini_assets = meeting.gemini_assets or existing.gemini_assets
                if meeting.calendar_metadata:
                    existing.calendar_metadata = meeting.calendar_metadata
                self.meeting_repo.upsert(existing)

        # Step 7: Update sync state
        self.sync_repo.update_calendar_check(count=len(meetings))

        logger.info(f"Discovery complete: {len(meetings)} meetings")
        return meetings

    def _fetch_calendar_events(
        self, after_date: str, before_date: str
    ) -> list[dict[str, Any]]:
        """Fetch calendar events via GWT."""
        calendar_id = self.config.get("calendar_id", "primary")
        try:
            events = self.gwt.get_calendar_events(
                time_min=after_date,
                time_max=before_date,
                calendar_id=calendar_id,
            )
            return events
        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {e}")
            raise

    def _find_gemini_assets(self, meeting: Meeting) -> GeminiAssets | None:
        """Search for Gemini transcript/summary emails matching a meeting."""
        query = f'from:gemini-notes@google.com subject:"{meeting.title}"'

        try:
            emails = self.gwt.search_gmail(query, max_results=10)
        except Exception as e:
            logger.warning(f"Gmail search failed for '{meeting.title}': {e}")
            return None

        if not emails:
            return None

        transcript = None
        summary = None

        for email in emails:
            subject = email.get("subject", "")
            doc_id = email.get("doc_id")

            if not doc_id:
                continue

            if "Notes by Gemini" in subject:
                transcript = GeminiAsset(
                    document_id=doc_id,
                    doc_url=f"https://docs.google.com/document/d/{doc_id}/edit",
                    email_id=email.get("thread_id"),
                )
            elif "Summary by Gemini" in subject:
                summary = GeminiAsset(
                    document_id=doc_id,
                    doc_url=f"https://docs.google.com/document/d/{doc_id}/edit",
                    email_id=email.get("thread_id"),
                )

        if transcript or summary:
            return GeminiAssets(transcript=transcript, summary=summary)

        return None

    def _find_orphaned_gemini_emails(
        self,
        after_date: str,
        before_date: str,
        matched_email_ids: set[str],
    ) -> list[Meeting]:
        """Find Gemini emails that don't match any calendar event.

        These represent meetings the user received notes for but wasn't invited to.
        """
        # Search for all Gemini emails in date range
        query = f"from:gemini-notes@google.com after:{after_date} before:{before_date}"

        try:
            emails = self.gwt.search_gmail(query, max_results=50)
        except Exception as e:
            logger.warning(f"Failed to search for orphaned emails: {e}")
            return []

        orphaned_meetings: list[Meeting] = []

        for email in emails:
            thread_id = email.get("thread_id", "")

            # Skip if already matched
            if thread_id in matched_email_ids:
                continue

            doc_id = email.get("doc_id")
            if not doc_id:
                continue

            subject = email.get("subject", "")

            # Extract meeting title from subject
            # Format: "Notes by Gemini: Meeting Title" or
            # "Summary by Gemini: Meeting Title"
            title_match = re.search(r"(?:Notes|Summary) by Gemini[:\s]+(.+)$", subject)  # noqa: E501
            if not title_match:
                continue

            meeting_title = title_match.group(1).strip()

            # Determine asset type
            asset_type = "transcript" if "Notes by Gemini" in subject else "summary"

            # Create meeting from orphaned email
            email_data = {
                "email_id": thread_id,
                "meeting_title": meeting_title,
                "doc_id": doc_id,
                "doc_url": f"https://docs.google.com/document/d/{doc_id}/edit",
                "asset_type": asset_type,
                "extracted_date": "",  # Could extract from email date
            }

            meeting = create_meeting_from_gemini_email(email_data)
            orphaned_meetings.append(meeting)

        return orphaned_meetings

    def _apply_pattern_or_generate_slug(self, meeting: Meeting) -> None:
        """Apply cached pattern or generate new slug for meeting."""
        # Check for cached pattern
        pattern = self.pattern_repo.find_matching_pattern(meeting.stable_id)

        if pattern:
            meeting.slug = pattern.slug
            meeting.is_recurring = pattern.is_recurring
            meeting.tag = pattern.tag
            logger.debug(
                f"Applied cached pattern: slug={meeting.slug}, "
                f"recurring={meeting.is_recurring}, tag={meeting.tag}"
            )

            # Update directory path
            if meeting.is_recurring is not None and meeting.tag is not None:
                meeting.directory = create_directory_path(meeting)
                meeting.status = "decided"

            # Update pattern count
            self.pattern_repo.update_pattern_count(meeting.stable_id, meeting.date)
        else:
            # Generate new slug
            attendees = []
            if meeting.calendar_metadata:
                attendees = meeting.calendar_metadata.attendees

            user_email = self.config.get("user_email")
            slug, is_one_on_one = generate_slug(meeting.title, attendees, user_email)

            meeting.slug = slug
            meeting.is_one_on_one = is_one_on_one
            meeting.status = "discovered"

            logger.debug(f"Generated slug: {slug} (one_on_one={is_one_on_one})")

    def get_pending_decisions(self) -> list[Meeting]:
        """Get meetings that need user decisions (recurring/tag)."""
        return self.meeting_repo.get_pending_decisions()

    def get_summary(self) -> dict[str, Any]:
        """Get summary of current discovery state."""
        counts = self.meeting_repo.count_by_status()
        sync_state = self.sync_repo.get_state()

        return {
            "total_meetings": self.meeting_repo.count(),
            "by_status": counts,
            "pending_decisions": len(self.get_pending_decisions()),
            "cached_patterns": self.pattern_repo.count_patterns(),
            "ignored_patterns": self.pattern_repo.count_ignored(),
            "last_calendar_check": sync_state.last_calendar_check,
            "last_email_check": sync_state.last_email_check,
            "total_processed": sync_state.total_processed,
        }
