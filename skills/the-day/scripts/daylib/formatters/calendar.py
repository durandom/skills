"""Calendar event formatter - replaces format-calendar.sh.

Parses calendar JSON and formats events as markdown.
"""

import json
import re
from datetime import datetime

from daylib.models import CalendarEvent

# Emoji rules based on event summary patterns
EMOJI_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"1:1|1-1|Marcel|/", re.IGNORECASE), "👥"),  # 1:1 meetings
    (re.compile(r"Breakfast|Coffee", re.IGNORECASE), "☕"),
    (re.compile(r"Lunch", re.IGNORECASE), "🍽️"),
    (re.compile(r"Office Hours|Support", re.IGNORECASE), "🔧"),
    (re.compile(r"Architecture|Tech Call", re.IGNORECASE), "🏗️"),
    (re.compile(r"Quality|QE|QA", re.IGNORECASE), "✅"),
    (re.compile(r"PM|Product|Leadership", re.IGNORECASE), "💼"),
    (re.compile(r"orchestrator", re.IGNORECASE), "🎯"),
    (re.compile(r"Home|PTO|OOO", re.IGNORECASE), "🏠"),
    (re.compile(r"#\d+"), "🎯"),  # Work blocks with issue numbers
]

DEFAULT_EMOJI = "📅"


def get_event_emoji(summary: str) -> str:
    """Determine emoji based on event summary.

    Args:
        summary: Event title/summary.

    Returns:
        Appropriate emoji for the event type.
    """
    for pattern, emoji in EMOJI_RULES:
        if pattern.search(summary):
            return emoji
    return DEFAULT_EMOJI


def parse_datetime(dt_string: str | None) -> datetime | None:
    """Parse datetime from ISO8601 string.

    Args:
        dt_string: ISO8601 datetime string.

    Returns:
        Parsed datetime or None.
    """
    if not dt_string:
        return None

    # Handle various ISO8601 formats
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",  # With timezone offset
        "%Y-%m-%dT%H:%M:%SZ",  # UTC
        "%Y-%m-%dT%H:%M:%S",  # No timezone
        "%Y-%m-%d",  # Date only (all-day events)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_string, fmt)
        except ValueError:
            continue

    # Fallback: try fromisoformat (Python 3.11+)
    try:
        return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_calendar_json(json_data: str | dict | list) -> list[CalendarEvent]:
    """Parse calendar JSON into CalendarEvent objects.

    Supports formats:
    - {"events": [...]} - wrapped array
    - [...] - direct array

    Each event should have:
    - summary: Event title
    - start: Start datetime (ISO8601)
    - end: End datetime (ISO8601)
    - link/htmlLink: Event URL
    - is_all_day/allDay: Boolean for all-day events

    Args:
        json_data: JSON string or parsed object.

    Returns:
        List of CalendarEvent objects.
    """
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Handle wrapped format
    if isinstance(data, dict):
        events_data = data.get("events", data.get("items", []))
    elif isinstance(data, list):
        events_data = data
    else:
        events_data = []

    events = []
    for item in events_data:
        summary = item.get("summary", item.get("title", "Untitled"))

        # Handle start/end which might be nested objects or strings
        start_raw = item.get("start")
        end_raw = item.get("end")

        if isinstance(start_raw, dict):
            start_str = start_raw.get("dateTime") or start_raw.get("date")
            all_day = "date" in start_raw and "dateTime" not in start_raw
        else:
            start_str = start_raw
            all_day = item.get("is_all_day", item.get("allDay", False))

        if isinstance(end_raw, dict):
            end_str = end_raw.get("dateTime") or end_raw.get("date")
        else:
            end_str = end_raw

        start = parse_datetime(start_str)
        end = parse_datetime(end_str)

        url = item.get("link") or item.get("htmlLink")
        location = item.get("location")
        emoji = get_event_emoji(summary)

        events.append(
            CalendarEvent(
                title=summary,
                start=start,
                end=end,
                all_day=all_day,
                location=location,
                url=url,
                emoji=emoji,
            )
        )

    # Sort: all-day first, then by start time
    events.sort(key=lambda e: (not e.all_day, e.start or datetime.min))

    return events


def format_event_markdown(event: CalendarEvent) -> str:
    """Format a single event as markdown.

    Args:
        event: CalendarEvent to format.

    Returns:
        Formatted markdown string.
    """
    lines = []

    if event.all_day:
        lines.append("- 🌅 **All Day**")
    elif event.start:
        start_time = event.start.strftime("%H:%M")
        if event.end:
            end_time = event.end.strftime("%H:%M")
            lines.append(f"- {start_time} - {end_time}")
        else:
            lines.append(f"- {start_time}")

    title_line = f"  {event.emoji} **{event.title}**"
    if event.url:
        title_line += f" [→]({event.url})"
    lines.append(title_line)

    if event.location:
        lines.append(f"  📍 {event.location}")

    return "\n".join(lines)


def format_calendar_events(
    events: list[CalendarEvent] | None = None,
    json_data: str | dict | list | None = None,
) -> str:
    """Format calendar events as markdown.

    Args:
        events: Pre-parsed events (if available).
        json_data: Raw JSON data (if events not provided).

    Returns:
        Formatted markdown string.
    """
    if events is None:
        if json_data is None:
            return "No calendar data provided"
        events = parse_calendar_json(json_data)

    if not events:
        return "No events found"

    lines = []
    for event in events:
        lines.append(format_event_markdown(event))

    return "\n\n".join(lines)
