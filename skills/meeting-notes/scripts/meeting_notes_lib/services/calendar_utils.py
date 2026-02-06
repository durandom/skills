"""
Calendar Utilities - Shared functions for calendar event processing.

This module extracts the duplicated code from CalendarDiscovery, EmailMatching,
and MeetingSync into standalone, testable functions.
"""

import logging
import re
from typing import Any

from ..models import CalendarMetadata, Meeting

logger = logging.getLogger(__name__)


def extract_stable_id(event: dict[str, Any]) -> str:
    """Extract stable identifier, normalizing recurring event IDs.

    For recurring events, strips the date suffix to get the base ID.
    This allows grouping all instances of a recurring meeting together.

    Pattern: {base_id}_R{YYYYMMDD}T{HHMMSS}
    Example: 99jl5pnjesqgus0or66vnb02g3_R20251201T150500 -> 99jl5pnjesqgus0or66vnb02g3

    Args:
        event: Calendar event dict from Google Calendar API

    Returns:
        Stable identifier string
    """
    stable_id = event.get("recurringEventId", event.get("id", ""))

    # For recurring events, strip date suffix to get base ID
    if "_R" in stable_id:
        parts = stable_id.split("_R")
        # Verify it's a date suffix (YYYYMMDDTHHMMSS = 15 chars)
        if len(parts) == 2 and len(parts[1]) >= 15:
            stable_id = parts[0]

    return stable_id


def should_include_event(
    event: dict[str, Any],
    processed_events: set[str] | None = None,
    ignored_stable_ids: set[str] | None = None,
) -> bool:
    """Filter logic for calendar events.

    Determines if a calendar event should be included in sync.

    Args:
        event: Calendar event dict
        processed_events: Set of already processed event IDs
        ignored_stable_ids: Set of stable IDs to ignore

    Returns:
        True if event should be included
    """
    event_id = event.get("id", "")
    stable_id = extract_stable_id(event)

    # Skip if already processed
    if processed_events and event_id in processed_events:
        logger.debug(f"Skipping already processed event: {event.get('summary')}")
        return False

    # Skip if in ignored list
    if ignored_stable_ids and stable_id in ignored_stable_ids:
        logger.debug(f"Skipping ignored event: {event.get('summary')}")
        return False

    # Skip all-day events without description
    start = event.get("start", {})
    if start.get("date") and not event.get("description"):
        logger.debug(
            f"Skipping all-day event without description: {event.get('summary')}"
        )
        return False

    # Include if >= 2 attendees
    attendees = event.get("attendees", [])
    if len(attendees) < 2:
        logger.debug(f"Skipping single-person event: {event.get('summary')}")
        return False

    return True


def extract_meeting_metadata(event: dict[str, Any]) -> Meeting:
    """Extract meeting metadata from calendar event.

    Creates a Meeting object with all relevant data from the calendar event.

    Args:
        event: Calendar event dict from Google Calendar API

    Returns:
        Meeting object with extracted metadata
    """
    stable_id = extract_stable_id(event)
    event_id = event.get("id", "")

    # Extract date and time
    start = event.get("start", {})
    if start.get("date"):
        # All-day event
        date = start["date"]
        time_str = ""
    else:
        # Timed event
        date_time = start.get("dateTime", "")
        date = date_time[:10] if date_time else ""
        time_str = date_time[11:16] if len(date_time) > 11 else ""

    # Extract calendar attachments
    calendar_attachments = []
    for att in event.get("attachments", []):
        calendar_attachments.append(
            {
                "title": att.get("title", ""),
                "file_id": att.get("fileId", ""),
                "file_url": att.get("fileUrl", ""),
                "mime_type": att.get("mimeType", ""),
            }
        )

    # Detect recurring from Google Calendar API
    # recurringEventId is present if this event is an instance of a recurring series
    is_recurring_from_api = "recurringEventId" in event or "recurrence" in event

    # Build calendar metadata
    calendar_metadata = CalendarMetadata(
        attendees=event.get("attendees", []),
        attendee_count=len(event.get("attendees", [])),
        description=event.get("description", ""),
        location=event.get("location", ""),
        calendar_link=event.get("htmlLink", ""),
        has_video_conference=event.get("conferenceData") is not None,
        organizer=event.get("organizer"),
        calendar_attachments=calendar_attachments,
        raw_event=event,
        is_api_recurring=is_recurring_from_api,
    )

    return Meeting(
        event_id=event_id,
        stable_id=stable_id,
        title=event.get("summary", "Untitled Meeting"),
        date=date,
        time=time_str,
        calendar_metadata=calendar_metadata,
        is_recurring=is_recurring_from_api,
    )


def generate_slug(
    title: str,
    attendees: list[dict[str, str]],
    user_email: str | None = None,
) -> tuple[str, bool]:
    """Generate context-rich slug from meeting title.

    For 1:1 meetings, uses the other attendee's email username.
    For other meetings, creates a slug from the title.

    Args:
        title: Meeting title
        attendees: List of attendee dicts with 'email' and 'displayName' keys
        user_email: Current user's email (to filter from 1:1 detection)

    Returns:
        Tuple of (slug, is_one_on_one)
    """
    title_lower = title.lower()

    # Detect 1:1 meetings by keywords OR attendee count
    is_one_on_one = (
        "1:1" in title_lower
        or "1-1" in title_lower
        or "one on one" in title_lower
        or len(attendees) == 2
    )

    if is_one_on_one:
        # Filter out current user from attendees
        other_attendees = attendees
        if user_email:
            user_email_lower = user_email.lower()
            other_attendees = [
                att
                for att in attendees
                if att.get("email", "").lower() != user_email_lower
            ]

        if other_attendees:
            att = other_attendees[0]

            # Use email username (before @)
            email = att.get("email", "")
            if email:
                name = email.split("@")[0]
                return name[:50], True

            # Fallback to display name
            display_name = att.get("displayName", "")
            if display_name:
                name = re.sub(r"[^a-z0-9]+", "-", display_name.lower()).strip("-")
                return name[:50], True

        # Fallback: use title-based slug
        slug = re.sub(r"[^a-z0-9]+", "-", title_lower).strip("-")
        return slug[:50], True

    # Generic slug from title
    slug = re.sub(r"[^a-z0-9]+", "-", title_lower).strip("-")
    return slug[:50], False


def create_directory_path(meeting: Meeting) -> str:
    """Create directory path for meeting output.

    Directory patterns:
        - One-on-one without transcript/summary: meetings/one-on-ones/{slug}/
        - One-on-one with transcript/summary: meetings/one-on-ones/{slug}/{date}/
        - Recurring with tag: meetings/{tag}/{slug}/{date}/
        - Recurring without tag: meetings/uncategorized/{slug}/{date}/
        - One-off with tag: meetings/{tag}/{date}-{slug}/
        - One-off without tag: meetings/uncategorized/{date}-{slug}/

    Args:
        meeting: Meeting object with classification data

    Returns:
        Directory path string
    """
    tag = meeting.tag or "uncategorized"

    # Special handling for one-on-ones
    if meeting.is_one_on_one:
        # Check if we have actual Gemini transcript or summary
        has_gemini_content = False
        if meeting.gemini_assets:
            has_gemini_content = (
                meeting.gemini_assets.transcript is not None
                or meeting.gemini_assets.summary is not None
            )

        # One-on-ones without Gemini content: no dated subdirectory
        if not has_gemini_content:
            return f"meetings/one-on-ones/{meeting.slug}"
        # One-on-ones with Gemini content: dated subdirectory
        return f"meetings/one-on-ones/{meeting.slug}/{meeting.date}"

    if meeting.is_recurring:
        # Recurring: meetings/{tag}/{slug}/YYYY-MM-DD/
        return f"meetings/{tag}/{meeting.slug}/{meeting.date}"

    # One-off: meetings/{tag}/YYYY-MM-DD-{slug}/
    return f"meetings/{tag}/{meeting.date}-{meeting.slug}"


def titles_match(calendar_title: str, email_title: str) -> bool:
    """Fuzzy match meeting titles for calendar/email matching.

    Performs case-insensitive, normalized comparison.
    Allows substring matches in either direction.

    Args:
        calendar_title: Title from calendar event
        email_title: Title from Gemini email

    Returns:
        True if titles match
    """

    def normalize(s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r"\s+", " ", s)  # Normalize whitespace
        s = s.replace("/", "-").replace(":", "")
        return s

    norm_cal = normalize(calendar_title)
    norm_email = normalize(email_title)

    # Exact match or substring match
    return norm_cal == norm_email or norm_cal in norm_email or norm_email in norm_cal


def create_meeting_from_gemini_email(email: dict[str, Any]) -> Meeting:
    """Create Meeting from orphaned Gemini email (no calendar event).

    Used for Gemini notes received for meetings the user wasn't invited to.

    Args:
        email: Parsed Gemini email dict with keys:
            - email_id: Email/thread ID
            - meeting_title: Extracted meeting title
            - doc_id: Google Doc ID
            - doc_url: Google Doc URL
            - asset_type: 'transcript' or 'summary'
            - extracted_date: Optional meeting date

    Returns:
        Meeting object marked as orphaned
    """
    from ..models import GeminiAsset, GeminiAssets

    date = email.get("extracted_date", "")
    stable_id = f"gemini_{email['email_id']}"

    # Create gemini assets
    asset = GeminiAsset(
        document_id=email["doc_id"],
        doc_url=email["doc_url"],
        email_id=email["email_id"],
        message_date=date,
    )

    gemini_assets = GeminiAssets()
    if email["asset_type"] == "transcript":
        gemini_assets.transcript = asset
    else:
        gemini_assets.summary = asset

    # Create placeholder calendar metadata
    calendar_metadata = CalendarMetadata(
        attendees=[],
        attendee_count=0,
    )

    return Meeting(
        event_id=stable_id,
        stable_id=stable_id,
        title=email["meeting_title"],
        date=date,
        time="",
        calendar_metadata=calendar_metadata,
        gemini_assets=gemini_assets,
        is_orphaned=True,
        status="discovered",
    )
