"""Unit tests for context module."""

import sys
from datetime import time
from pathlib import Path

import pytest

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent / "skills" / "layton"),
)

from laytonlib.context import (
    classify_time_of_day,
    format_human_context,
    is_within_work_hours,
    parse_time,
)


class TestClassifyTimeOfDay:
    """Tests for time of day classification."""

    @pytest.mark.parametrize(
        "hour,expected",
        [
            (5, "morning"),
            (6, "morning"),
            (11, "morning"),
            (12, "midday"),
            (13, "midday"),
            (14, "afternoon"),
            (17, "afternoon"),
            (18, "evening"),
            (21, "evening"),
            (22, "night"),
            (23, "night"),
            (0, "night"),
            (4, "night"),
        ],
    )
    def test_classification(self, hour: int, expected: str):
        """Test all time boundaries."""
        assert classify_time_of_day(hour) == expected


class TestParseTime:
    """Tests for time parsing."""

    def test_parse_simple(self):
        """Parse simple time."""
        result = parse_time("09:00")
        assert result == time(9, 0)

    def test_parse_with_minutes(self):
        """Parse time with minutes."""
        result = parse_time("17:30")
        assert result == time(17, 30)


class TestIsWithinWorkHours:
    """Tests for work hours calculation."""

    def test_within_hours(self):
        """Time within work hours."""
        current = time(10, 30)
        assert is_within_work_hours(current, "09:00", "17:00") is True

    def test_at_start_boundary(self):
        """Time exactly at start is within."""
        current = time(9, 0)
        assert is_within_work_hours(current, "09:00", "17:00") is True

    def test_at_end_boundary(self):
        """Time exactly at end is within."""
        current = time(17, 0)
        assert is_within_work_hours(current, "09:00", "17:00") is True

    def test_before_start(self):
        """Time before start is outside."""
        current = time(8, 59)
        assert is_within_work_hours(current, "09:00", "17:00") is False

    def test_after_end(self):
        """Time after end is outside."""
        current = time(17, 1)
        assert is_within_work_hours(current, "09:00", "17:00") is False


class TestFormatHumanContext:
    """Tests for human-readable formatting."""

    def test_work_hours(self):
        """Format during work hours."""
        context = {
            "day_of_week": "Monday",
            "time_of_day": "morning",
            "work_hours": True,
        }
        result = format_human_context(context)
        assert "Monday morning" in result
        assert "within work hours" in result

    def test_outside_work_hours(self):
        """Format outside work hours."""
        context = {
            "day_of_week": "Saturday",
            "time_of_day": "evening",
            "work_hours": False,
        }
        result = format_human_context(context)
        assert "Saturday evening" in result
        assert "outside work hours" in result
