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


@pytest.fixture
def temp_skills_dir(isolated_env):
    """Temporary .layton/skills/ directory for isolated tests."""
    skills_dir = isolated_env / ".layton" / "skills"
    skills_dir.mkdir(exist_ok=True)
    return skills_dir


@pytest.fixture
def temp_workflows_dir(isolated_env):
    """Temporary .layton/workflows/ directory for isolated tests."""
    workflows_dir = isolated_env / ".layton" / "workflows"
    workflows_dir.mkdir(exist_ok=True)
    return workflows_dir


@pytest.fixture
def temp_skills_root(isolated_env):
    """Temporary skills/ directory (for skill discovery tests)."""
    skills_root = isolated_env / "skills"
    skills_root.mkdir(exist_ok=True)
    return skills_root


@pytest.fixture
def sample_skill_file(temp_skills_dir):
    """Create a sample skill file for testing."""
    skill_path = temp_skills_dir / "sample.md"
    skill_path.write_text("""---
name: sample
description: A sample skill for testing
source: skills/sample/SKILL.md
---

## Commands

```bash
sample --help
```

## What to Extract

- Important data
- Key metrics

## Key Metrics

| Metric | Meaning |
|--------|---------|
| count  | Number of items |
""")
    return skill_path


@pytest.fixture
def sample_workflow_file(temp_workflows_dir):
    """Create a sample workflow file for testing."""
    workflow_path = temp_workflows_dir / "sample.md"
    workflow_path.write_text("""---
name: sample
description: A sample workflow for testing
triggers:
  - run sample
  - test workflow
---

## Objective

Test the workflow system.

## Steps

1. Get context:
   ```bash
   layton context
   ```

2. Do something

## Context Adaptation

- If morning: do morning things
- If evening: do evening things

## Success Criteria

- [ ] Task completed
- [ ] No errors
""")
    return workflow_path
