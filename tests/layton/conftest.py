"""Shared pytest fixtures for Layton tests."""

import shutil
from pathlib import Path  # noqa: F401 - used in type hints

import pytest


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Fully isolated environment with temp .layton/ and .beads/."""
    # Create isolated directories
    layton_dir = tmp_path / ".layton"
    layton_dir.mkdir()
    beads_dir = tmp_path / ".beads"
    beads_dir.mkdir()

    # Change working directory to temp (isolates bd auto-detection)
    monkeypatch.chdir(tmp_path)

    return tmp_path


@pytest.fixture
def temp_config(isolated_env):
    """Temporary .layton/config.json for isolated tests."""
    config_path = isolated_env / ".layton" / "config.json"
    return config_path


@pytest.fixture
def mock_beads_available(monkeypatch):
    """Mock bd CLI availability check (unit tests only)."""
    monkeypatch.setattr(
        shutil,
        "which",
        lambda cmd: "/usr/bin/bd" if cmd == "bd" else None,
    )


@pytest.fixture
def mock_beads_unavailable(monkeypatch):
    """Mock bd CLI as unavailable (unit tests only)."""
    monkeypatch.setattr(shutil, "which", lambda cmd: None)


@pytest.fixture
def real_beads_isolated(isolated_env):
    """Real bd CLI in isolated temp directory (integration tests)."""
    # bd will auto-init in isolated_env/.beads/ on first write
    return isolated_env / ".beads"
