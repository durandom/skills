"""Shared fixtures for GTD tests."""

import sys
from pathlib import Path

import pytest

# Add gtdlib to import path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "skills/gtd/scripts"))


@pytest.fixture
def gtd_dir(tmp_path):
    """Create an isolated .gtd directory for testing."""
    d = tmp_path / ".gtd"
    d.mkdir()
    return d
