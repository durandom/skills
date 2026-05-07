"""
Data Models for Meeting Notes

Dataclasses representing meetings, sync state, and patterns.
All models can be serialized to/from JSONL records.
"""

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Schema version for forward compatibility
MODEL_VERSION = 1


# --- Configuration ---


@dataclass
class GWTConfig:
    """gwt tool configuration (credentials stored in keyring)."""

    gwt_path: Path
    gwt_command: str
    gwt_output_dir: Path
    debug: bool = False  # Pass --debug to gwt commands

    @classmethod
    def from_config(cls, config: dict, debug: bool = False) -> "GWTConfig":
        """Load from config dict."""
        return cls(
            gwt_path=Path(config["gwt_path"]),
            gwt_command=config["gwt_command"],
            gwt_output_dir=Path(config["gwt_output_dir"]),
            debug=debug,
        )


# --- Meeting Models ---


@dataclass
class CalendarAttachment:
    """Calendar-attached document metadata."""

    title: str
    file_id: str
    file_url: str
    mime_type: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "CalendarAttachment":
        return cls(**data)


@dataclass
class GeminiAsset:
    """Gemini transcript or summary metadata."""

    document_id: str
    doc_url: str
    email_id: str | None = None
    message_date: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GeminiAsset":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class GeminiAssets:
    """Container for Gemini transcript and summary."""

    transcript: GeminiAsset | None = None
    summary: GeminiAsset | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {}
        if self.transcript:
            result["transcript"] = self.transcript.to_dict()
        if self.summary:
            result["summary"] = self.summary.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GeminiAssets":
        return cls(
            transcript=GeminiAsset.from_dict(data["transcript"])
            if data.get("transcript")
            else None,
            summary=GeminiAsset.from_dict(data["summary"])
            if data.get("summary")
            else None,
        )


@dataclass
class CalendarMetadata:
    """Metadata extracted from calendar event."""

    attendees: list[dict[str, str]] = field(default_factory=list)
    attendee_count: int = 0
    description: str = ""
    calendar_link: str = ""
    has_video_conference: bool = False
    location: str = ""
    organizer: dict[str, str] | None = None
    calendar_attachments: list[dict[str, Any]] = field(default_factory=list)
    raw_event: dict[str, Any] | None = None  # Original event data (not serialized)
    is_api_recurring: bool | None = None  # True if Google Calendar says it's recurring

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        # Don't serialize raw_event to save space
        result.pop("raw_event", None)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CalendarMetadata":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Meeting:
    """Core meeting entity.

    This is the primary model for meetings stored in the JSONL database.
    """

    # Required identifiers
    stable_id: str  # Stable identifier (normalized from recurring events)
    event_id: str  # Original Google Calendar event ID

    # Core data
    title: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format

    # Classification (set during decide phase)
    slug: str | None = None
    tag: str | None = None  # e.g., 'rhdh', 'one-on-ones', 'team'
    is_recurring: bool | None = None
    is_recurring_override: bool = False  # True if user manually set recurring flag
    is_one_on_one: bool = False

    # Status tracking
    status: str = "discovered"  # discovered | decided | downloading | synced | error
    directory: str | None = None  # Output path when synced

    # Related data
    calendar_metadata: CalendarMetadata | None = None
    gemini_assets: GeminiAssets | None = None

    # Flags
    manual_capture_needed: bool = False
    is_orphaned: bool = False  # Gemini email without calendar event

    # Alias support: links multiple calendar events to one logical meeting
    alias_of: str | None = None  # stable_id of primary meeting

    # Version for schema evolution
    version: int = MODEL_VERSION

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSONL storage."""
        result = {
            "stable_id": self.stable_id,
            "event_id": self.event_id,
            "title": self.title,
            "date": self.date,
            "time": self.time,
            "slug": self.slug,
            "tag": self.tag,
            "is_recurring": self.is_recurring,
            "is_recurring_override": self.is_recurring_override,
            "is_one_on_one": self.is_one_on_one,
            "status": self.status,
            "directory": self.directory,
            "manual_capture_needed": self.manual_capture_needed,
            "is_orphaned": self.is_orphaned,
            "alias_of": self.alias_of,
            "version": self.version,
        }
        if self.calendar_metadata:
            result["calendar_metadata"] = self.calendar_metadata.to_dict()
        if self.gemini_assets:
            result["gemini_assets"] = self.gemini_assets.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Meeting":
        """Create from dictionary (JSONL record data field)."""
        calendar_metadata = None
        if data.get("calendar_metadata"):
            calendar_metadata = CalendarMetadata.from_dict(data["calendar_metadata"])

        gemini_assets = None
        if data.get("gemini_assets"):
            gemini_assets = GeminiAssets.from_dict(data["gemini_assets"])

        return cls(
            stable_id=data["stable_id"],
            event_id=data.get("event_id", data["stable_id"]),
            title=data["title"],
            date=data["date"],
            time=data.get("time", ""),
            slug=data.get("slug"),
            tag=data.get("tag"),
            is_recurring=data.get("is_recurring"),
            is_recurring_override=data.get("is_recurring_override", False),
            is_one_on_one=data.get("is_one_on_one", False),
            status=data.get("status", "discovered"),
            directory=data.get("directory"),
            calendar_metadata=calendar_metadata,
            gemini_assets=gemini_assets,
            manual_capture_needed=data.get("manual_capture_needed", False),
            is_orphaned=data.get("is_orphaned", False),
            alias_of=data.get("alias_of"),
            version=data.get("version", MODEL_VERSION),
        )


# --- Pattern Models ---


@dataclass
class RecurringPattern:
    """Cached recurring meeting decision.

    Stores user decisions about how to classify meetings with similar titles.
    """

    stable_id: str
    slug: str
    title_pattern: str
    is_recurring: bool
    tag: str | None = None
    count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    calendar_attachments: list[dict[str, Any]] = field(default_factory=list)
    version: int = MODEL_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecurringPattern":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class IgnoredPattern:
    """Meetings to ignore in future syncs."""

    stable_id: str
    title_pattern: str | None = None
    reason: str = "user_ignored"
    ignored_at: str = ""
    version: int = MODEL_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IgnoredPattern":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# --- Tag Definitions ---


@dataclass
class Tag:
    """Tag definition with metadata.

    Tags categorize meetings (e.g., 'rhdh', 'one-on-ones', 'team').
    This model stores tag definitions with optional metadata.
    """

    name: str  # Tag identifier (stable_id in JSONL)
    description: str = ""
    color: str | None = None  # Hex color, e.g., "#e63946"
    created_at: str = ""
    updated_at: str = ""
    version: int = MODEL_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Tag":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# --- Sync State ---


@dataclass
class SyncState:
    """Sync process state.

    Tracks when syncs happened and processing counts.
    """

    last_calendar_check: str | None = None
    last_email_check: str | None = None
    last_sync_count: int = 0
    total_processed: int = 0
    version: int = MODEL_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SyncState":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# --- Legacy Compatibility ---

# INTENT: Alias for backwards compatibility with old code
MeetingDiscovery = Meeting
