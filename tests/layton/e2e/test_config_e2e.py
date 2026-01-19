"""E2E tests for layton config commands."""

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


class TestConfigInit:
    """E2E tests for config init."""

    def test_init_creates_config(self, isolated_env):
        """init creates config file."""
        config_path = isolated_env / ".layton" / "config.json"
        assert not config_path.exists()

        result = run_layton("config", "init", cwd=isolated_env)

        assert result.returncode == 0
        assert config_path.exists()

        # Verify JSON structure
        data = json.loads(result.stdout)
        assert data["success"] is True

    def test_init_fails_if_exists(self, isolated_env):
        """init fails if config exists."""
        config_path = isolated_env / ".layton" / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("{}")

        result = run_layton("config", "init", cwd=isolated_env)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["success"] is False
        assert data["error"]["code"] == "CONFIG_EXISTS"

    def test_init_force_overwrites(self, isolated_env):
        """init --force overwrites existing."""
        config_path = isolated_env / ".layton" / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text('{"old": "value"}')

        result = run_layton("config", "init", "--force", cwd=isolated_env)

        assert result.returncode == 0

        # Verify new config has defaults
        config = json.loads(config_path.read_text())
        assert "timezone" in config


class TestConfigShow:
    """E2E tests for config show."""

    def test_show_displays_config(self, isolated_env):
        """show displays config content."""
        # Create config first
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("config", "show", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "config" in data["data"]

    def test_show_fails_if_missing(self, isolated_env):
        """show fails if no config."""
        result = run_layton("config", "show", cwd=isolated_env)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "CONFIG_MISSING"

    def test_config_no_subcommand_runs_show(self, isolated_env):
        """config with no subcommand runs show."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("config", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "config" in data["data"]


class TestConfigKeys:
    """E2E tests for config keys."""

    def test_keys_lists_paths(self, isolated_env):
        """keys lists all dot-notation paths."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("config", "keys", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        keys = data["data"]["keys"]
        assert "timezone" in keys
        assert "work.schedule.start" in keys


class TestConfigGet:
    """E2E tests for config get."""

    def test_get_flat_key(self, isolated_env):
        """get retrieves flat key."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("config", "get", "timezone", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["key"] == "timezone"

    def test_get_nested_key(self, isolated_env):
        """get retrieves nested key."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("config", "get", "work.schedule.start", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["value"] == "09:00"

    def test_get_missing_key(self, isolated_env):
        """get fails for missing key."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton("config", "get", "nonexistent", cwd=isolated_env)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "KEY_NOT_FOUND"


class TestConfigSet:
    """E2E tests for config set."""

    def test_set_updates_value(self, isolated_env):
        """set updates existing value."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton(
            "config", "set", "timezone", "Europe/London", cwd=isolated_env
        )

        assert result.returncode == 0

        # Verify change
        result = run_layton("config", "get", "timezone", cwd=isolated_env)
        data = json.loads(result.stdout)
        assert data["data"]["value"] == "Europe/London"

    def test_set_creates_nested_path(self, isolated_env):
        """set creates nested path."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton(
            "config", "set", "custom.nested.key", "value", cwd=isolated_env
        )

        assert result.returncode == 0

        # Verify
        result = run_layton("config", "get", "custom.nested.key", cwd=isolated_env)
        data = json.loads(result.stdout)
        assert data["data"]["value"] == "value"

    def test_set_parses_json(self, isolated_env):
        """set parses JSON values."""
        run_layton("config", "init", cwd=isolated_env)

        result = run_layton(
            "config",
            "set",
            "work.schedule",
            '{"start": "08:00", "end": "16:00"}',
            cwd=isolated_env,
        )

        assert result.returncode == 0

        # Verify
        result = run_layton("config", "get", "work.schedule.start", cwd=isolated_env)
        data = json.loads(result.stdout)
        assert data["data"]["value"] == "08:00"
