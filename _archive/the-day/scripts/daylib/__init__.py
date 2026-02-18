"""Day CLI library for daily overview generation.

This library provides deterministic components for the-day skill:
- GTD task formatting
- Calendar event formatting
- TODAY.md archiving
- Template generation

AI-driven components (weather, email categorization, inspiration)
remain in SKILL.md.
"""

from daylib.models import CalendarEvent, DayStatus, GTDTask

__all__ = ["DayStatus", "GTDTask", "CalendarEvent"]
