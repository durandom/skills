"""E2E tests for layton doctor command."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


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


class TestDoctorCommand:
    """E2E tests for layton doctor."""

    def test_doctor_outputs_json(self, isolated_env, mock_beads_unavailable):
        """doctor outputs valid JSON by default."""
        result = run_layton("doctor", cwd=isolated_env)

        # Should be valid JSON regardless of exit code
        try:
            data = json.loads(result.stdout)
            assert "success" in data or "error" in data
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {result.stdout}")

    def test_doctor_no_args_runs_doctor(self, isolated_env):
        """layton with no args runs doctor."""
        result = run_layton(cwd=isolated_env)

        # Should produce JSON output (doctor command)
        try:
            data = json.loads(result.stdout)
            # Doctor either succeeds with checks or fails with error
            assert "success" in data or "error" in data
        except json.JSONDecodeError:
            pytest.fail(f"Output is not valid JSON: {result.stdout}")

    def test_doctor_fix_creates_config(self, isolated_env):
        """doctor --fix creates config when missing."""
        config_path = isolated_env / ".layton" / "config.json"
        assert not config_path.exists()

        result = run_layton("doctor", "--fix", cwd=isolated_env)

        # If beads is available, config should be created
        # If beads is not available, it will fail before fixing config
        if result.returncode != 2:  # Not critical beads failure
            assert config_path.exists()

    def test_doctor_human_output(self, isolated_env):
        """doctor --human outputs human-readable format."""
        result = run_layton("doctor", "--human", cwd=isolated_env)

        # Human output should NOT be JSON
        try:
            json.loads(result.stdout)
            # If it parses as JSON, that's wrong for human mode
            # (unless it's an empty response)
            if result.stdout.strip():
                pytest.fail("Human output should not be JSON")
        except json.JSONDecodeError:
            pass  # Expected - human output is not JSON

    def test_doctor_fix_hidden_from_help(self, isolated_env):
        """--fix flag should be hidden from help output."""
        result = run_layton("doctor", "--help", cwd=isolated_env)

        # --fix should NOT appear in help
        assert "--fix" not in result.stdout

    def test_doctor_exit_code_on_missing_config(self, isolated_env):
        """doctor returns exit code 1 when config missing (if beads available)."""
        result = run_layton("doctor", cwd=isolated_env)

        # Exit code 1 = fixable (config missing) or 2 = critical (beads missing)
        assert result.returncode in (1, 2)
