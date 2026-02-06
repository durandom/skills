"""Archive service - replaces archive-today.sh.

Extracts timestamp from TODAY.md and archives to logs/today/.
"""

import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Pattern to match timestamp line in TODAY.md
# Example: "*Generated at 09:46 CET on Wednesday, January 8, 2026*"
TIMESTAMP_PATTERN = re.compile(
    r"\*Generated at (\d{2}):(\d{2}) \w+ on \w+, (\w+) (\d{1,2}), (\d{4})\*"
)

# Month name to number mapping
MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


@dataclass
class ArchiveResult:
    """Result of archive operation."""

    success: bool
    source_path: Path | None = None
    archive_path: Path | None = None
    message: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "success": self.success,
            "source_path": str(self.source_path) if self.source_path else None,
            "archive_path": str(self.archive_path) if self.archive_path else None,
            "message": self.message,
        }


def extract_timestamp(content: str) -> datetime | None:
    """Extract timestamp from TODAY.md content.

    Args:
        content: File content to parse.

    Returns:
        Extracted datetime or None if not found.
    """
    match = TIMESTAMP_PATTERN.search(content)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))
    month_name = match.group(3)
    day = int(match.group(4))
    year = int(match.group(5))

    month = MONTHS.get(month_name)
    if month is None:
        return None

    try:
        return datetime(year, month, day, hour, minute)
    except ValueError:
        return None


def archive_today(
    today_path: Path,
    archive_dir: Path,
    dry_run: bool = False,
) -> ArchiveResult:
    """Archive TODAY.md to logs/today/.

    Args:
        today_path: Path to TODAY.md file.
        archive_dir: Directory for archived files.
        dry_run: If True, don't actually move the file.

    Returns:
        ArchiveResult with success status and paths.
    """
    if not today_path.exists():
        return ArchiveResult(
            success=True,
            message=f"No {today_path.name} found to archive",
        )

    # Read content to extract timestamp
    content = today_path.read_text()
    timestamp = extract_timestamp(content)

    # Use extracted timestamp or fall back to current time
    if timestamp:
        archive_name = timestamp.strftime("%Y-%m-%d-%H%M.md")
    else:
        archive_name = datetime.now().strftime("%Y-%m-%d-%H%M.md")

    archive_path = archive_dir / archive_name

    if dry_run:
        return ArchiveResult(
            success=True,
            source_path=today_path,
            archive_path=archive_path,
            message=f"Would archive {today_path.name} → {archive_path}",
        )

    # Create archive directory if needed
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Handle collision (same timestamp exists)
    if archive_path.exists():
        # Add counter to filename
        counter = 1
        while archive_path.exists():
            stem = archive_name.rsplit(".", 1)[0]
            archive_path = archive_dir / f"{stem}-{counter}.md"
            counter += 1

    # Move file
    shutil.move(str(today_path), str(archive_path))

    return ArchiveResult(
        success=True,
        source_path=today_path,
        archive_path=archive_path,
        message=f"Archived {today_path.name} → {archive_path.name}",
    )
