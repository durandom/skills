"""Shared fixtures for PARA tests."""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest


def _import_para():
    """Import the para CLI script as a module.

    The para script has no .py extension (it's an executable CLI), so we use
    importlib with an explicit SourceFileLoader to load it as a module.
    """
    script = Path(__file__).parent.parent.parent / "skills/para/scripts/para"
    loader = importlib.machinery.SourceFileLoader("para_cli", str(script))
    spec = importlib.util.spec_from_file_location("para_cli", script, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    # Avoid polluting sys.modules across tests
    old = sys.modules.get("para_cli")
    try:
        spec.loader.exec_module(mod)
    finally:
        if old is not None:
            sys.modules["para_cli"] = old
        else:
            sys.modules.pop("para_cli", None)
    return mod


@pytest.fixture
def para():
    """Import the para CLI script as a testable module."""
    return _import_para()
