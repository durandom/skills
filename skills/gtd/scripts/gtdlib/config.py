"""GTD configuration loading.

Handles loading and saving `.gtd.json` configuration files which specify
backend choice and backend-specific settings.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

CONFIG_DIR = ".gtd"
CONFIG_FILENAME = "config.json"
AVAILABLE_BACKENDS = ["github", "taskwarrior", "beads"]


@dataclass
class TaskwarriorConfig:
    """Taskwarrior backend configuration."""

    data_dir: str = ".gtd/taskwarrior"


@dataclass
class GitHubConfig:
    """GitHub backend configuration."""

    repo: str | None = None


@dataclass
class BeadsBackendConfig:
    """Beads backend configuration."""

    # Beads uses bd CLI which auto-discovers .beads/ directory
    # No additional config needed - bd handles everything
    pass


@dataclass
class GTDConfig:
    """GTD skill configuration."""

    backend: Literal["github", "taskwarrior", "beads"] = "github"
    taskwarrior: TaskwarriorConfig = field(default_factory=TaskwarriorConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    beads: BeadsBackendConfig = field(default_factory=BeadsBackendConfig)


def get_git_root() -> Path | None:
    """Get the root of the current git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def find_config_file(start_dir: Path | None = None) -> Path | None:
    """Find .gtd/config.json in git root or cwd (repo-local only).

    Only checks:
    1. Git root (if in a git repo)
    2. Current working directory

    Does NOT walk up parent directories to avoid finding stray configs.

    Args:
        start_dir: Directory to start searching from. Defaults to cwd.

    Returns:
        Path to config file if found, None otherwise.
    """
    cwd = (start_dir or Path.cwd()).resolve()

    # Check git root first (most common case for repo-local config)
    git_root = get_git_root()
    if git_root:
        config_path = git_root / CONFIG_DIR / CONFIG_FILENAME
        if config_path.exists():
            return config_path

    # Fallback to cwd (for non-git directories)
    config_path = cwd / CONFIG_DIR / CONFIG_FILENAME
    if config_path.exists():
        return config_path

    return None


def load_config(config_path: Path | None = None) -> GTDConfig:
    """Load GTD configuration from file or return defaults.

    Args:
        config_path: Explicit path to config file. If None, uses
            find_config_file to look for `.gtd/config.json` in the git
            repository root (if any) or the current working directory.

    Returns:
        GTDConfig with loaded or default values.
    """
    if config_path is None:
        config_path = find_config_file()

    if config_path is None or not config_path.exists():
        return GTDConfig()

    try:
        data = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        return GTDConfig()

    # Build config from parsed data
    backend = data.get("backend", "github")
    if backend not in AVAILABLE_BACKENDS:
        backend = "github"

    # Ensure backend-specific config sections are dicts before unpacking
    tw_data = data.get("taskwarrior", {})
    if not isinstance(tw_data, dict):
        tw_data = {}
    gh_data = data.get("github", {})
    if not isinstance(gh_data, dict):
        gh_data = {}
    beads_data = data.get("beads", {})
    if not isinstance(beads_data, dict):
        beads_data = {}

    # Construct backend configs defensively; fall back to defaults on error
    try:
        tw_config = TaskwarriorConfig(**tw_data)
    except TypeError:
        tw_config = TaskwarriorConfig()

    try:
        gh_config = GitHubConfig(**gh_data)
    except TypeError:
        gh_config = GitHubConfig()

    try:
        beads_config = BeadsBackendConfig(**beads_data)
    except TypeError:
        beads_config = BeadsBackendConfig()

    return GTDConfig(
        backend=backend,
        taskwarrior=tw_config,
        github=gh_config,
        beads=beads_config,
    )


def detect_skill_directory(cwd: Path | None = None) -> bool:
    """Detect if cwd is the skill directory itself (Pattern 3).

    Checks for a fingerprint of SKILL.md + scripts/ which indicates the user
    is running from the skill's own source directory, not a project.
    """
    cwd = cwd or Path.cwd()
    fingerprint = ["SKILL.md", "scripts"]
    return all((cwd / f).exists() for f in fingerprint)


def is_initialized() -> bool:
    """Check if GTD has been initialized (config file exists)."""
    return find_config_file() is not None


def get_config_save_path() -> Path:
    """Get the path where config should be saved (.gtd/config.json).

    Prefers git root if in a repo, otherwise uses cwd.
    Creates .gtd/ directory if needed.
    """
    git_root = get_git_root()
    base = git_root if git_root else Path.cwd()
    config_dir = base / CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILENAME


def save_config(config: GTDConfig, path: Path | None = None) -> Path:
    """Save GTD configuration to file.

    Args:
        config: Configuration to save.
        path: Explicit path. If None, uses get_config_save_path().

    Returns:
        Path where config was saved.
    """
    if path is None:
        path = get_config_save_path()

    data: dict = {"backend": config.backend}

    # Only include backend-specific config if non-default
    if config.backend == "taskwarrior":
        if config.taskwarrior.data_dir != ".gtd/taskwarrior":
            data["taskwarrior"] = {"data_dir": config.taskwarrior.data_dir}
    elif config.backend == "github":
        if config.github.repo:
            data["github"] = {"repo": config.github.repo}

    path.write_text(json.dumps(data, indent=2) + "\n")
    return path
