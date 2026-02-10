"""GTD review tracking.

Tracks when reviews (daily/weekly/quarterly/yearly) were last completed.
Stores timestamps in `.gtd/reviews.json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from gtdlib.config import CONFIG_DIR, get_git_root

REVIEWS_FILENAME = "reviews.json"

# Review cadences in days
REVIEW_CADENCES = {
    "daily": 1,
    "weekly": 7,
    "quarterly": 90,
    "yearly": 365,
}

ReviewType = str  # "daily" | "weekly" | "quarterly" | "yearly"


@dataclass
class ReviewHistory:
    """Timestamps for when each review type was last completed."""

    daily: datetime | None = None
    weekly: datetime | None = None
    quarterly: datetime | None = None
    yearly: datetime | None = None


def _get_reviews_path() -> Path:
    """Get path to reviews.json file."""
    git_root = get_git_root()
    base = git_root if git_root else Path.cwd()
    return base / CONFIG_DIR / REVIEWS_FILENAME


def load_reviews() -> ReviewHistory:
    """Load review history from .gtd/reviews.json.

    Returns:
        ReviewHistory with loaded timestamps, or empty history if file doesn't exist.
    """
    path = _get_reviews_path()
    if not path.exists():
        return ReviewHistory()

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return ReviewHistory()

    def parse_dt(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            return None

    return ReviewHistory(
        daily=parse_dt(data.get("daily")),
        weekly=parse_dt(data.get("weekly")),
        quarterly=parse_dt(data.get("quarterly")),
        yearly=parse_dt(data.get("yearly")),
    )


def save_reviews(history: ReviewHistory) -> Path:
    """Save review history to .gtd/reviews.json.

    Args:
        history: Review history to save.

    Returns:
        Path where history was saved.
    """
    path = _get_reviews_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    def fmt_dt(dt: datetime | None) -> str | None:
        return dt.isoformat() if dt else None

    data = {
        "daily": fmt_dt(history.daily),
        "weekly": fmt_dt(history.weekly),
        "quarterly": fmt_dt(history.quarterly),
        "yearly": fmt_dt(history.yearly),
    }

    # Only include non-null values
    data = {k: v for k, v in data.items() if v is not None}
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def mark_review_complete(review_type: ReviewType) -> datetime:
    """Mark a review as completed now.

    Args:
        review_type: One of "daily", "weekly", "quarterly", "yearly".

    Returns:
        The timestamp recorded.
    """
    history = load_reviews()
    now = datetime.now()

    if review_type == "daily":
        history.daily = now
    elif review_type == "weekly":
        history.weekly = now
    elif review_type == "quarterly":
        history.quarterly = now
    elif review_type == "yearly":
        history.yearly = now

    save_reviews(history)
    return now


def reset_review(review_type: ReviewType) -> None:
    """Reset a review timestamp (for testing).

    Args:
        review_type: One of "daily", "weekly", "quarterly", "yearly".
    """
    history = load_reviews()

    if review_type == "daily":
        history.daily = None
    elif review_type == "weekly":
        history.weekly = None
    elif review_type == "quarterly":
        history.quarterly = None
    elif review_type == "yearly":
        history.yearly = None

    save_reviews(history)


@dataclass
class DueReview:
    """A review that is due or overdue."""

    review_type: str
    days_overdue: int  # 0 = due today, >0 = overdue
    last_done: datetime | None
    workflow_path: str = field(default="")


def get_due_reviews() -> list[DueReview]:
    """Get list of reviews that are due or overdue.

    Returns:
        List of DueReview objects sorted by urgency (most overdue first).
    """
    history = load_reviews()
    now = datetime.now()
    due = []

    for review_type, cadence_days in REVIEW_CADENCES.items():
        last_done = getattr(history, review_type)

        if last_done is None:
            # Never done - definitely overdue
            days_overdue = cadence_days  # Treat as one full cadence overdue
        else:
            days_since = (now - last_done).days
            if days_since >= cadence_days:
                days_overdue = days_since - cadence_days + 1
            else:
                continue  # Not due yet

        due.append(
            DueReview(
                review_type=review_type,
                days_overdue=days_overdue,
                last_done=last_done,
                workflow_path=f".claude/skills/gtd/references/{review_type}-review.md",
            )
        )

    # Sort by urgency (most overdue first)
    return sorted(due, key=lambda r: -r.days_overdue)


def get_review_status() -> dict[str, dict]:
    """Get status of all reviews for display.

    Returns:
        Dict mapping review type to status info with keys:
        last_done (datetime|None), days_ago (int|None),
        due_in (int), overdue (bool).
    """
    history = load_reviews()
    now = datetime.now()
    status = {}

    for review_type, cadence_days in REVIEW_CADENCES.items():
        last_done = getattr(history, review_type)

        if last_done is None:
            status[review_type] = {
                "last_done": None,
                "days_ago": None,
                "due_in": 0,
                "overdue": True,
            }
        else:
            days_since = (now - last_done).days
            due_in = cadence_days - days_since

            status[review_type] = {
                "last_done": last_done,
                "days_ago": days_since,
                "due_in": due_in,
                "overdue": due_in <= 0,
            }

    return status
