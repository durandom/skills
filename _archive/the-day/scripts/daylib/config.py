"""Configuration and path discovery for the day CLI."""

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DayConfig:
    """Configuration for the day CLI."""

    repo_root: Path
    gtd_cli_path: Path
    template_path: Path
    today_md_path: Path
    logs_dir: Path
    timezone: str = "Europe/Berlin"

    @classmethod
    def discover(cls) -> "DayConfig":
        """Discover configuration from git root."""
        repo_root = find_repo_root()
        if not repo_root:
            repo_root = Path.cwd()

        # GTD CLI is in skills/gtd/scripts/gtd relative to CLAUDE.md location
        # The skill is at .claude/skills/the-day/ or skills/the-day/
        # GTD is at .claude/skills/gtd/ or skills/gtd/
        gtd_cli_path = find_gtd_cli(repo_root)

        # Template is in the-day skill directory
        skill_dir = find_skill_dir(repo_root)
        template_path = skill_dir / "templates" / "today.md.template"

        return cls(
            repo_root=repo_root,
            gtd_cli_path=gtd_cli_path,
            template_path=template_path,
            today_md_path=repo_root / "TODAY.md",
            logs_dir=repo_root / "logs" / "today",
            timezone="Europe/Berlin",
        )


def find_repo_root() -> Path | None:
    """Find the git repository root."""
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


def find_gtd_cli(repo_root: Path) -> Path:
    """Find the GTD CLI script.

    Searches common locations:
    - .claude/skills/gtd/scripts/gtd (standard)
    - skills/gtd/scripts/gtd (development)
    """
    candidates = [
        repo_root / ".claude" / "skills" / "gtd" / "scripts" / "gtd",
        repo_root / "skills" / "gtd" / "scripts" / "gtd",
    ]

    for path in candidates:
        if path.exists():
            return path

    # Fallback: assume it's in PATH
    return Path("gtd")


def find_skill_dir(repo_root: Path) -> Path:
    """Find the-day skill directory.

    Searches common locations:
    - .claude/skills/the-day/ (standard)
    - skills/the-day/ (development)
    """
    candidates = [
        repo_root / ".claude" / "skills" / "the-day",
        repo_root / "skills" / "the-day",
    ]

    for path in candidates:
        if path.exists():
            return path

    # Fallback to relative to this file
    return Path(__file__).parent.parent.parent


def is_gtd_initialized(config: DayConfig) -> bool:
    """Check if GTD is initialized."""
    gtd_config = config.repo_root / ".gtd" / "config.json"
    return gtd_config.exists()


def today_md_exists(config: DayConfig) -> bool:
    """Check if TODAY.md exists."""
    return config.today_md_path.exists()
