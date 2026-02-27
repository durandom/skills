"""GTD storage backends.

Backend classes:
- GitHubStorage: GitHub Issues via gh CLI
- TaskwarriorStorage: Taskwarrior via task CLI
- BeadsStorage: Beads via bd CLI (lazy import to avoid failure when bd not installed)
"""

from .github import GitHubStorage
from .taskwarrior import TaskwarriorStorage

__all__ = ["GitHubStorage", "TaskwarriorStorage", "BeadsStorage"]  # pyright: ignore[reportUnsupportedDunderAll]


def get_backend_class(name: str):
    """Get backend class by name. Supports lazy loading.

    Args:
        name: Backend name ("github", "taskwarrior", "beads").

    Returns:
        The backend class.

    Raises:
        ValueError: If name is not a valid backend.
    """
    if name == "github":
        return GitHubStorage
    elif name == "taskwarrior":
        return TaskwarriorStorage
    elif name == "beads":
        from .beads import BeadsStorage

        return BeadsStorage
    else:
        raise ValueError(f"Unknown backend: {name!r}")
