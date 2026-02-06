"""
Service layer for Meeting Notes.

Business logic organized into focused service classes.
"""

from .calendar_utils import (
    create_directory_path,
    extract_meeting_metadata,
    extract_stable_id,
    generate_slug,
    should_include_event,
    titles_match,
)
from .decision import DecisionService
from .discovery import DiscoveryService
from .downloads import DownloadService
from .output_sync import OutputSyncService

__all__ = [
    # Utilities
    "extract_stable_id",
    "should_include_event",
    "extract_meeting_metadata",
    "generate_slug",
    "create_directory_path",
    "titles_match",
    # Services
    "DiscoveryService",
    "DecisionService",
    "DownloadService",
    "OutputSyncService",
]
