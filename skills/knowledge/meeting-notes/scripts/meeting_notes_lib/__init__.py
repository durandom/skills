"""
Meeting Notes Library - JSONL database and services for meeting_notes.
"""

__version__ = "2.0.0"

from .db import MeetingNotesDB
from .gwt import GWTInvoker
from .models import GWTConfig, Meeting, Tag

__all__ = ["MeetingNotesDB", "GWTInvoker", "Meeting", "GWTConfig", "Tag"]
