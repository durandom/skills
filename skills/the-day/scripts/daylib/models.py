"""Data models for the day CLI.

Dataclass-based models with to_dict() for JSON serialization.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class GTDTask:
    """A GTD task from the gtd CLI output."""

    id: int
    title: str
    context: str | None = None  # focus, async, meetings, offsite
    energy: str | None = None  # high, low
    status: str | None = None  # active, waiting, someday
    project: str | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "context": self.context,
            "energy": self.energy,
            "status": self.status,
            "project": self.project,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GTDTask":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            context=data.get("context"),
            energy=data.get("energy"),
            status=data.get("status"),
            project=data.get("project"),
            url=data.get("url"),
        )


@dataclass
class CalendarEvent:
    """A calendar event."""

    title: str
    start: datetime | None = None
    end: datetime | None = None
    all_day: bool = False
    location: str | None = None
    url: str | None = None
    emoji: str = "📅"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "start": self.start.isoformat() if self.start else None,
            "end": self.end.isoformat() if self.end else None,
            "all_day": self.all_day,
            "location": self.location,
            "url": self.url,
            "emoji": self.emoji,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CalendarEvent":
        """Create from dictionary."""
        return cls(
            title=data["title"],
            start=datetime.fromisoformat(data["start"]) if data.get("start") else None,
            end=datetime.fromisoformat(data["end"]) if data.get("end") else None,
            all_day=data.get("all_day", False),
            location=data.get("location"),
            url=data.get("url"),
            emoji=data.get("emoji", "📅"),
        )


@dataclass
class GTDSection:
    """A section of GTD tasks grouped by context/energy."""

    title: str
    emoji: str
    tasks: list[GTDTask] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "emoji": self.emoji,
            "tasks": [t.to_dict() for t in self.tasks],
        }


@dataclass
class DayStatus:
    """Status of the current day for the CLI."""

    date: date
    today_md_exists: bool = False
    today_md_path: str | None = None
    gtd_initialized: bool = False
    gtd_task_count: int = 0
    gtd_high_energy: int = 0
    gtd_low_energy: int = 0
    calendar_event_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date.isoformat(),
            "today_md_exists": self.today_md_exists,
            "today_md_path": self.today_md_path,
            "gtd_initialized": self.gtd_initialized,
            "gtd_tasks": {
                "total": self.gtd_task_count,
                "high_energy": self.gtd_high_energy,
                "low_energy": self.gtd_low_energy,
            },
            "calendar_events": self.calendar_event_count,
        }
