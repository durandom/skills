"""GTD action history logging.

Append-only JSONL log of GTD actions for tracking and analysis.
Stores entries in `.gtd/history.log`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from gtdlib.config import CONFIG_DIR, get_git_root

HISTORY_FILENAME = "history.log"


@dataclass
class HistoryEntry:
    """A single action logged to history."""

    ts: datetime
    action: str
    item_id: str | None = None
    title: str | None = None
    labels: list[str] | None = None
    review_type: str | None = None
    extra: dict | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        d: dict[str, Any] = {
            "ts": self.ts.isoformat(),
            "action": self.action,
        }
        if self.item_id:
            d["item_id"] = self.item_id
        if self.title:
            d["title"] = self.title
        if self.labels:
            d["labels"] = self.labels
        if self.review_type:
            d["type"] = self.review_type
        if self.extra:
            d.update(self.extra)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> HistoryEntry:
        """Create from dict."""
        ts_str = d.get("ts", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            ts = datetime.now()

        return cls(
            ts=ts,
            action=d.get("action", "unknown"),
            item_id=d.get("item_id"),
            title=d.get("title"),
            labels=d.get("labels"),
            review_type=d.get("type"),
            extra={
                k: v
                for k, v in d.items()
                if k not in ("ts", "action", "item_id", "title", "labels", "type")
            },
        )


def _get_history_path() -> Path:
    """Get path to history.log file."""
    git_root = get_git_root()
    base = git_root if git_root else Path.cwd()
    return base / CONFIG_DIR / HISTORY_FILENAME


def log_action(
    action: str,
    item_id: str | None = None,
    title: str | None = None,
    labels: list[str] | None = None,
    review_type: str | None = None,
    **extra: Any,
) -> HistoryEntry:
    """Log an action to history.

    Args:
        action: Action type (capture, clarify, done, review, etc.)
        item_id: Optional item ID affected.
        title: Optional item title.
        labels: Optional list of labels assigned.
        review_type: Optional review type (daily, weekly, etc.)
        **extra: Additional fields to include.

    Returns:
        The logged entry.
    """
    path = _get_history_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = HistoryEntry(
        ts=datetime.now(),
        action=action,
        item_id=item_id,
        title=title,
        labels=labels,
        review_type=review_type,
        extra=extra if extra else None,
    )

    # Append as JSONL
    with path.open("a") as f:
        f.write(json.dumps(entry.to_dict()) + "\n")

    return entry


def read_history(
    limit: int = 20,
    since: date | None = None,
) -> list[HistoryEntry]:
    """Read history entries.

    Args:
        limit: Maximum entries to return (most recent first).
        since: Only include entries on or after this date.

    Returns:
        List of history entries, most recent first.
    """
    path = _get_history_path()
    if not path.exists():
        return []

    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            entry = HistoryEntry.from_dict(d)

            # Apply date filter
            if since and entry.ts.date() < since:
                continue

            entries.append(entry)
        except json.JSONDecodeError:
            continue

    # Most recent first
    entries.reverse()

    # Apply limit
    if limit > 0:
        entries = entries[:limit]

    return entries


def format_entry_human(entry: HistoryEntry) -> str:
    """Format an entry for human-readable display."""
    time_str = entry.ts.strftime("%Y-%m-%d %H:%M")
    parts = [time_str, entry.action]

    if entry.review_type:
        parts.append(f"({entry.review_type})")
    if entry.item_id:
        parts.append(f"#{entry.item_id}")
    if entry.title:
        # Truncate long titles
        title = entry.title[:40] + "..." if len(entry.title) > 40 else entry.title
        parts.append(f'"{title}"')

    return " ".join(parts)
