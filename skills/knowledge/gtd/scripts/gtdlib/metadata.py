"""GTD metadata parsing and serialization.

Handles machine-readable metadata stored in issue bodies as HTML comments:
<!-- gtd-metadata: {"due":"2026-01-15",...} -->

This format is:
- Invisible in rendered GitHub markdown
- Machine-parseable JSON
- Won't conflict with existing body content
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date

# Regex pattern for finding metadata comment
# Matches: <!-- gtd-metadata: {...JSON...} -->
METADATA_PATTERN = re.compile(r"<!-- gtd-metadata: ({.*?}) -->", re.DOTALL)


@dataclass
class GTDMetadata:
    """Machine-readable GTD metadata embedded in issue body.

    Fields:
        due: Due date for the item
        defer_until: Don't surface until this date
        waiting_for: Who/what we're waiting on {"person": str, "reason": str}
        blocked_by: List of issue numbers blocking this item
    """

    due: date | None = None
    defer_until: date | None = None
    waiting_for: dict | None = None  # {"person": str, "reason": str}
    blocked_by: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        result = {}
        if self.due:
            result["due"] = self.due.isoformat()
        if self.defer_until:
            result["defer_until"] = self.defer_until.isoformat()
        if self.waiting_for:
            result["waiting_for"] = self.waiting_for
        if self.blocked_by:
            result["blocked_by"] = self.blocked_by
        return result

    def to_comment(self) -> str:
        """Serialize to HTML comment string."""
        data = self.to_dict()
        return f"<!-- gtd-metadata: {json.dumps(data, separators=(',', ':'))} -->"

    def is_empty(self) -> bool:
        """Check if all fields are empty/None."""
        return (
            self.due is None
            and self.defer_until is None
            and self.waiting_for is None
            and not self.blocked_by
        )


def parse_metadata(body: str | None) -> GTDMetadata:
    """Extract GTDMetadata from issue body.

    Args:
        body: Issue body content (may be None or empty)

    Returns:
        GTDMetadata instance (empty if no metadata found or parsing fails)
    """
    if not body:
        return GTDMetadata()

    match = METADATA_PATTERN.search(body)
    if not match:
        return GTDMetadata()

    try:
        data = json.loads(match.group(1))
        return GTDMetadata(
            due=date.fromisoformat(data["due"]) if data.get("due") else None,
            defer_until=(
                date.fromisoformat(data["defer_until"])
                if data.get("defer_until")
                else None
            ),
            waiting_for=data.get("waiting_for"),
            blocked_by=data.get("blocked_by", []),
        )
    except (json.JSONDecodeError, ValueError, KeyError):
        # Malformed metadata - return empty (defensive)
        return GTDMetadata()


def update_body_metadata(body: str | None, metadata: GTDMetadata) -> str:
    """Update or insert metadata comment in body.

    Args:
        body: Current issue body (may be None or empty)
        metadata: New metadata to embed

    Returns:
        Updated body with metadata comment
    """
    body = body or ""

    if metadata.is_empty():
        # Remove existing metadata comment if present
        return METADATA_PATTERN.sub("", body).strip()

    comment = metadata.to_comment()

    if METADATA_PATTERN.search(body):
        # Replace existing metadata
        return METADATA_PATTERN.sub(comment, body)
    else:
        # Insert at beginning (visible in edit mode, hidden in render)
        if body.strip():
            return f"{comment}\n\n{body}"
        return comment


def is_deferred(metadata: GTDMetadata) -> bool:
    """Check if item is currently deferred (defer_until in future).

    Args:
        metadata: GTDMetadata instance

    Returns:
        True if defer_until is set and in the future
    """
    if not metadata.defer_until:
        return False
    return metadata.defer_until > date.today()


def is_overdue(metadata: GTDMetadata) -> bool:
    """Check if item is past due date.

    Args:
        metadata: GTDMetadata instance

    Returns:
        True if due date is set and in the past
    """
    if not metadata.due:
        return False
    return metadata.due < date.today()


def is_due_before(metadata: GTDMetadata, target: date) -> bool:
    """Check if item is due on or before target date.

    Args:
        metadata: GTDMetadata instance
        target: Date to compare against

    Returns:
        True if due date is set and <= target
    """
    if not metadata.due:
        return False
    return metadata.due <= target
