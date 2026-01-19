"""E2E tests for layton context command."""

import json
import subprocess
import sys
from pathlib import Path


def run_layton(*args, cwd=None):
    """Run layton CLI and return result."""
    script_path = (
        Path(__file__).parent.parent.parent.parent
        / "skills"
        / "layton"
        / "scripts"
        / "layton"
    )
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result


class TestContextCommand:
    """E2E tests for layton context."""

    def test_context_requires_config(self, isolated_env):
        """context fails if no config."""
        result = run_layton("context", cwd=isolated_env)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "CONFIG_MISSING"

    def test_context_outputs_json(self, isolated_env):
        """context outputs valid JSON with config."""
        # Create config
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("context", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True

        # Check required fields
        context = data["data"]
        assert "timestamp" in context
        assert "time_of_day" in context
        assert "day_of_week" in context
        assert "work_hours" in context
        assert "timezone" in context

    def test_context_time_of_day_valid(self, isolated_env):
        """context returns valid time_of_day."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("context", cwd=isolated_env)

        data = json.loads(result.stdout)
        tod = data["data"]["time_of_day"]
        assert tod in ["morning", "midday", "afternoon", "evening", "night"]

    def test_context_human_output(self, isolated_env):
        """context --human includes summary."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("--human", "context", cwd=isolated_env)

        # Human output should include day and time of day
        assert result.returncode == 0
        # Human output is not JSON, should have readable text
        output = result.stdout
        # Should mention day of week somewhere
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        assert any(day in output for day in days)

    def test_context_respects_timezone(self, isolated_env):
        """context uses timezone from config."""
        run_layton("config", "init", cwd=isolated_env)
        run_layton("config", "set", "timezone", "America/Los_Angeles", cwd=isolated_env)

        result = run_layton("context", cwd=isolated_env)

        data = json.loads(result.stdout)
        assert data["data"]["timezone"] == "America/Los_Angeles"
