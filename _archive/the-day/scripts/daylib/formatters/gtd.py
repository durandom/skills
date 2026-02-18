"""GTD task formatter - replaces format-gtd-tasks.sh (142 lines AWK).

Parses GTD CLI output and formats tasks into structured sections.
"""

import re
import subprocess
from pathlib import Path

from daylib.models import GTDSection, GTDTask

# ANSI escape code pattern
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

# Section header pattern: @context (N items)
SECTION_HEADER = re.compile(r"^@(\w+)")

# Task line pattern: #ID Title [metadata]
# Example: #42 Write RFE draft [context/focus E:high S:active P:project-name]
TASK_LINE = re.compile(
    r"^\s*#(\d+)\s+(.+?)\s+\["
    r"(?:context/(\w+))?\s*"
    r"(?:E:(\w+))?\s*"
    r"(?:S:(\w+))?\s*"
    r"(?:P:([^\]]+))?"
    r"\]"
)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return ANSI_ESCAPE.sub("", text)


def parse_gtd_output(output: str, github_repo: str | None = None) -> list[GTDTask]:
    """Parse GTD CLI output into a list of tasks.

    Args:
        output: Raw output from `gtd list` command.
        github_repo: Optional GitHub repo for URL generation (e.g., "owner/repo").

    Returns:
        List of GTDTask objects.
    """
    tasks = []
    clean_output = strip_ansi(output)
    current_context = None

    for line in clean_output.splitlines():
        # Stop at "Next steps:" section
        if line.startswith("Next steps:"):
            break

        # Check for section header
        header_match = SECTION_HEADER.match(line)
        if header_match:
            current_context = header_match.group(1)
            continue

        # Check for task line
        task_match = TASK_LINE.match(line)
        if task_match:
            task_id = int(task_match.group(1))
            title = task_match.group(2).strip()
            context = task_match.group(3) or current_context
            energy = task_match.group(4)
            status = task_match.group(5)
            project = task_match.group(6)

            # Build URL if repo is provided
            url = None
            if github_repo:
                url = f"https://github.com/{github_repo}/issues/{task_id}"

            tasks.append(
                GTDTask(
                    id=task_id,
                    title=title,
                    context=context,
                    energy=energy,
                    status=status,
                    project=project.strip() if project else None,
                    url=url,
                )
            )

    return tasks


def group_tasks_by_section(tasks: list[GTDTask]) -> list[GTDSection]:
    """Group tasks into sections by context and energy.

    Sections:
    - Focus Work (High Energy): context=focus, energy=high
    - Async Work: context=async
    - Light Focus (Low Energy): context=focus, energy=low
    - Meeting Prep: context=meetings
    """
    focus_high = []
    focus_low = []
    async_tasks = []
    meeting_tasks = []
    other_tasks = []

    for task in tasks:
        if task.context == "focus":
            if task.energy == "high":
                focus_high.append(task)
            else:
                focus_low.append(task)
        elif task.context == "async":
            async_tasks.append(task)
        elif task.context == "meetings":
            meeting_tasks.append(task)
        else:
            other_tasks.append(task)

    sections = []

    if focus_high:
        sections.append(GTDSection("Focus Work (High Energy)", "🔥", focus_high))

    if async_tasks:
        sections.append(GTDSection("Async Work", "🔄", async_tasks))

    if focus_low:
        sections.append(GTDSection("Light Focus (Low Energy)", "📝", focus_low))

    if meeting_tasks:
        sections.append(GTDSection("Meeting Prep", "👥", meeting_tasks))

    if other_tasks:
        sections.append(GTDSection("Other Tasks", "📋", other_tasks))

    return sections


def format_task_markdown(task: GTDTask) -> str:
    """Format a single task as markdown."""
    if task.url:
        line = f"- [#{task.id}]({task.url}) - **{task.title}**"
    else:
        line = f"- #{task.id} - **{task.title}**"

    if task.project:
        line += f"\n  `project/{task.project}`"

    return line


def format_section_markdown(section: GTDSection) -> str:
    """Format a section as markdown."""
    lines = [f"### {section.emoji} {section.title}", ""]
    for task in section.tasks:
        lines.append(format_task_markdown(task))
    lines.append("")
    return "\n".join(lines)


def format_gtd_tasks(
    tasks: list[GTDTask] | None = None,
    output: str | None = None,
    github_repo: str | None = None,
) -> str:
    """Format GTD tasks as markdown sections.

    Args:
        tasks: Pre-parsed tasks (if available).
        output: Raw GTD CLI output (if tasks not provided).
        github_repo: GitHub repo for URL generation.

    Returns:
        Formatted markdown string.
    """
    if tasks is None:
        if output is None:
            return "No tasks provided"
        tasks = parse_gtd_output(output, github_repo)

    if not tasks:
        return "No active tasks found"

    sections = group_tasks_by_section(tasks)

    if not sections:
        return "No active tasks found"

    return "\n".join(format_section_markdown(s) for s in sections)


def run_gtd_list(gtd_cli_path: Path, status: str = "active") -> str | None:
    """Run the GTD CLI and return output.

    Args:
        gtd_cli_path: Path to the gtd CLI script.
        status: Status filter (default: active).

    Returns:
        Command output or None if failed.
    """
    try:
        result = subprocess.run(
            [str(gtd_cli_path), "list", "--status", status],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except FileNotFoundError:
        return None


def get_github_repo_from_gtd_config(repo_root: Path) -> str | None:
    """Read GitHub repo from GTD config.

    Args:
        repo_root: Repository root path.

    Returns:
        GitHub repo string (e.g., "owner/repo") or None.
    """
    import json

    config_path = repo_root / ".gtd" / "config.json"
    if not config_path.exists():
        return None

    try:
        with open(config_path) as f:
            config = json.load(f)
        return config.get("github", {}).get("repo")
    except (json.JSONDecodeError, OSError):
        return None
