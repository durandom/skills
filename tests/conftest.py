"""Pytest configuration with syrupy snapshot testing."""

import pytest
from syrupy.extensions.amber import AmberSnapshotExtension


@pytest.fixture
def snapshot(snapshot):
    """Configure syrupy to use Amber extension for readable multi-line snapshots."""
    return snapshot.use_extension(AmberSnapshotExtension)
