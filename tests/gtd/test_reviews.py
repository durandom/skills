"""Tests for GTD review tracking."""

import json
from datetime import datetime, timedelta
from unittest.mock import patch

from gtdlib.reviews import (
    ReviewHistory,
    get_due_reviews,
    get_review_status,
    load_reviews,
    mark_review_complete,
    reset_review,
    save_reviews,
)


class TestReviewPersistence:
    """Test save/load of review timestamps."""

    def test_load_missing_file_returns_empty(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            history = load_reviews()
        assert history.daily is None
        assert history.weekly is None

    def test_save_and_load_roundtrip(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        now = datetime(2026, 2, 16, 10, 0)
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            save_reviews(ReviewHistory(daily=now, weekly=now))
            loaded = load_reviews()
        assert loaded.daily == now
        assert loaded.weekly == now
        assert loaded.quarterly is None

    def test_save_omits_null_values(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        path.parent.mkdir(parents=True)
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            save_reviews(ReviewHistory(daily=datetime(2026, 2, 16, 10, 0)))
        data = json.loads(path.read_text())
        assert "daily" in data
        assert "weekly" not in data

    def test_load_corrupt_json_returns_empty(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        path.parent.mkdir(parents=True)
        path.write_text("not json")
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            history = load_reviews()
        assert history.daily is None


class TestMarkAndReset:
    """Test marking reviews complete and resetting."""

    def test_mark_review_complete(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            ts = mark_review_complete("daily")
        assert ts is not None
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            loaded = load_reviews()
        assert loaded.daily is not None

    def test_reset_review(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            mark_review_complete("weekly")
            reset_review("weekly")
            loaded = load_reviews()
        assert loaded.weekly is None


class TestGetDueReviews:
    """Test due review detection."""

    def test_never_done_reviews_are_due(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            due = get_due_reviews()
        # All 4 review types should be due (never done)
        types = {r.review_type for r in due}
        assert types == {"daily", "weekly", "quarterly", "yearly"}

    def test_recently_done_review_not_due(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            mark_review_complete("daily")
            due = get_due_reviews()
        types = {r.review_type for r in due}
        assert "daily" not in types

    def test_overdue_sorted_by_urgency(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        now = datetime.now()
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            # Weekly: 14d ago (7 overdue), daily: 3d ago (2 overdue)
            save_reviews(
                ReviewHistory(
                    daily=now - timedelta(days=3),
                    weekly=now - timedelta(days=14),
                )
            )
            due = get_due_reviews()
        # Filter to only daily and weekly (quarterly/yearly are also due)
        daily_weekly = [r for r in due if r.review_type in ("daily", "weekly")]
        assert len(daily_weekly) == 2
        # Weekly should be more overdue than daily
        assert daily_weekly[0].review_type == "weekly"


class TestGetReviewStatus:
    """Test review status reporting."""

    def test_never_done_is_overdue(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            status = get_review_status()
        assert status["daily"]["overdue"] is True
        assert status["daily"]["last_done"] is None

    def test_recently_done_not_overdue(self, tmp_path):
        path = tmp_path / ".gtd" / "reviews.json"
        with patch("gtdlib.reviews._get_reviews_path", return_value=path):
            mark_review_complete("daily")
            status = get_review_status()
        assert status["daily"]["overdue"] is False
        assert status["daily"]["days_ago"] == 0
