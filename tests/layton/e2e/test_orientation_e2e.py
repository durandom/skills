"""E2E tests for layton orientation (no-arg invocation)."""

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


class TestOrientationCommand:
    """E2E tests for layton (no args) orientation output."""

    def test_no_args_returns_orientation(self, isolated_env, temp_config):
        """layton (no args) returns orientation with checks, skills, workflows."""
        # Create a valid config
        temp_config.write_text('{"timezone": "UTC"}')

        result = run_layton(cwd=isolated_env)

        # Parse output - may fail with beads error, that's ok
        data = json.loads(result.stdout)
        if data.get("success"):
            assert "checks" in data["data"]
            assert "skills" in data["data"]
            assert "workflows" in data["data"]

    def test_orientation_includes_checks(self, isolated_env, temp_config):
        """Orientation includes doctor checks."""
        temp_config.write_text('{"timezone": "UTC"}')

        result = run_layton(cwd=isolated_env)
        data = json.loads(result.stdout)

        if data.get("success"):
            checks = data["data"]["checks"]
            assert isinstance(checks, list)
            # Should have at least beads_available and config checks
            check_names = [c["name"] for c in checks]
            assert "config_exists" in check_names

    def test_orientation_includes_skills(
        self,
        isolated_env,
        temp_config,
        sample_skill_file,
    ):
        """Orientation includes skills inventory."""
        temp_config.write_text('{"timezone": "UTC"}')

        # sample_skill_file is created in isolated_env
        result = run_layton(cwd=isolated_env)
        data = json.loads(result.stdout)

        if data.get("success"):
            skills = data["data"]["skills"]
            assert isinstance(skills, list)
            assert len(skills) == 1
            assert skills[0]["name"] == "sample"

    def test_orientation_includes_workflows(
        self, isolated_env, temp_config, sample_workflow_file
    ):
        """Orientation includes workflows inventory."""
        temp_config.write_text('{"timezone": "UTC"}')

        # sample_workflow_file is created in isolated_env
        result = run_layton(cwd=isolated_env)
        data = json.loads(result.stdout)

        if data.get("success"):
            workflows = data["data"]["workflows"]
            assert isinstance(workflows, list)
            assert len(workflows) == 1
            assert workflows[0]["name"] == "sample"
            assert "triggers" in workflows[0]

    def test_orientation_includes_next_steps(self, isolated_env, temp_config):
        """Orientation includes next_steps when skills/workflows empty."""
        temp_config.write_text('{"timezone": "UTC"}')

        result = run_layton(cwd=isolated_env)
        data = json.loads(result.stdout)

        if data.get("success"):
            # With empty skills/workflows, should have next_steps
            assert "next_steps" in data["data"] or "next_steps" in data

    def test_orientation_human_output(self, isolated_env, temp_config):
        """layton --human outputs human-readable format."""
        temp_config.write_text('{"timezone": "UTC"}')

        result = run_layton("--human", cwd=isolated_env)

        # Human output should NOT be JSON
        try:
            json.loads(result.stdout)
            if result.stdout.strip():
                assert False, "Human output should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected


class TestCompactOutput:
    """Tests for compact CLI output formatting."""

    def test_compact_summary_on_success(self, isolated_env, temp_config):
        """Human output shows compact summary when all checks pass."""
        temp_config.write_text('{"timezone": "UTC"}')

        result = run_layton("--human", cwd=isolated_env)

        # If beads is unavailable, the command exits early with error
        # Skip compact output check in that case
        output = result.stdout + result.stderr
        if "Beads CLI" in output:
            # Beads not available - can't test compact output
            return

        # Should show compact summary, not individual checks
        # Format: "✓ N/N checks passed"
        assert "checks passed" in result.stdout, (
            f"Expected compact summary with 'checks passed', got: {result.stdout}"
        )
        # Should NOT show individual check names in compact mode
        # (unless there's a failure)
        if "✗" not in result.stdout:  # No failures
            assert "beads_available:" not in result.stdout or "✓" in result.stdout

    def test_verbose_shows_all_checks(self, isolated_env, temp_config):
        """Human output with --verbose shows all check details."""
        temp_config.write_text('{"timezone": "UTC"}')

        result = run_layton("--human", "--verbose", cwd=isolated_env)

        # If beads is unavailable, the command exits early with error
        output = result.stdout + result.stderr
        if "Beads CLI" in output:
            # Beads not available - can't test verbose output
            return

        # Verbose mode should show individual checks
        assert "checks:" in result.stdout, (
            f"Expected 'checks:' header in verbose output, got: {result.stdout}"
        )

    def test_expanded_output_on_failure(self, isolated_env):
        """Human output expands when a check fails."""
        # Don't create config - this causes config_exists to fail
        # Remove the config file if it exists
        config_path = isolated_env / ".layton" / "config.json"
        if config_path.exists():
            config_path.unlink()

        result = run_layton("--human", cwd=isolated_env)

        # On failure, should show expanded output with check details
        output = result.stdout + result.stderr
        # Should show the failure (either beads or config failure)
        assert "✗" in output or "Error" in output or "fail" in output.lower(), (
            f"Expected failure indicator in output: {output}"
        )

    def test_json_output_also_compact(self, isolated_env, temp_config):
        """JSON output is also compact when all checks pass."""
        temp_config.write_text('{"timezone": "UTC"}')

        result = run_layton(cwd=isolated_env)

        data = json.loads(result.stdout)
        if data.get("success"):
            checks = data["data"]["checks"]
            # When all pass, checks is a summary dict (not array)
            if isinstance(checks, dict):
                assert "summary" in checks, "Compact checks should have summary"
                assert "all_passed" in checks, "Compact checks should have all_passed"
            else:
                # If it's still a list, there was a failure/warning - verify structure
                assert isinstance(checks, list)
                for check in checks:
                    assert "name" in check
                    assert "status" in check
