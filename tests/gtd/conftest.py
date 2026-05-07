"""Shared fixtures for GTD tests."""

import sys
from pathlib import Path

import pytest

# Add gtdlib to import path
_GTD_SCRIPTS = Path(__file__).parent.parent.parent / "skills/knowledge/gtd/scripts"
sys.path.insert(0, str(_GTD_SCRIPTS))


@pytest.fixture
def gtd_dir(tmp_path):
    """Create an isolated .gtd directory for testing."""
    d = tmp_path / ".gtd"
    d.mkdir()
    return d
