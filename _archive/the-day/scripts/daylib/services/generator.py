"""Generator service - TODAY.md template rendering.

Fills deterministic placeholders in the template:
- {{DATE_FULL}} - Full date string
- {{TIME}} - Current time with timezone
- {{LOCATION}} - Location name
- {{GTD_TASKS}} - Formatted GTD tasks

Leaves AI placeholders for SKILL.md to fill:
- {{WEATHER_CONTENT}}
- {{CALENDAR_EVENTS}} (MCP-dependent)
- {{STARRED_EMAILS}}
- {{INSPIRATION}}
- {{WIKIPEDIA_ARTICLE}}
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Placeholder pattern
PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class GenerateResult:
    """Result of generate operation."""

    success: bool
    output_path: Path | None = None
    content: str = ""
    filled_placeholders: list[str] = field(default_factory=list)
    remaining_placeholders: list[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "success": self.success,
            "output_path": str(self.output_path) if self.output_path else None,
            "filled_placeholders": self.filled_placeholders,
            "remaining_placeholders": self.remaining_placeholders,
            "message": self.message,
        }


def get_date_full(timezone: str = "Europe/Berlin") -> str:
    """Get full date string (e.g., 'Monday, January 13, 2025')."""
    try:
        tz = ZoneInfo(timezone)
    except KeyError:
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)
    return now.strftime("%A, %B %d, %Y")


def get_time_string(timezone: str = "Europe/Berlin") -> str:
    """Get time string with timezone abbreviation (e.g., '09:46 CET')."""
    try:
        tz = ZoneInfo(timezone)
    except KeyError:
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)
    # Get timezone abbreviation
    tz_abbr = now.strftime("%Z") or "UTC"
    return f"{now.strftime('%H:%M')} {tz_abbr}"


def find_placeholders(content: str) -> list[str]:
    """Find all placeholders in content."""
    return list(set(PLACEHOLDER.findall(content)))


def fill_template(
    template_content: str,
    values: dict[str, str],
) -> tuple[str, list[str], list[str]]:
    """Fill template placeholders with values.

    Args:
        template_content: Template string with {{PLACEHOLDER}} markers.
        values: Dictionary of placeholder -> value mappings.

    Returns:
        Tuple of (filled_content, filled_placeholders, remaining_placeholders).
    """
    filled = []
    remaining = []

    def replace_placeholder(match: re.Match) -> str:
        name = match.group(1)
        if name in values:
            filled.append(name)
            return values[name]
        else:
            remaining.append(name)
            return match.group(0)  # Keep original

    result = PLACEHOLDER.sub(replace_placeholder, template_content)
    return result, filled, list(set(remaining))


def generate_today(
    template_path: Path,
    output_path: Path,
    gtd_tasks: str = "",
    location: str = "Kiel, Germany",
    timezone: str = "Europe/Berlin",
    dry_run: bool = False,
    extra_values: dict[str, str] | None = None,
) -> GenerateResult:
    """Generate TODAY.md from template.

    Fills deterministic placeholders and optionally writes to file.
    AI-driven placeholders are left for SKILL.md to fill.

    Args:
        template_path: Path to template file.
        output_path: Path to write output (TODAY.md).
        gtd_tasks: Pre-formatted GTD tasks markdown.
        location: Location name for weather header.
        timezone: Timezone for date/time formatting.
        dry_run: If True, don't write file, just return content.
        extra_values: Additional placeholder values to fill.

    Returns:
        GenerateResult with filled content and metadata.
    """
    if not template_path.exists():
        return GenerateResult(
            success=False,
            message=f"Template not found: {template_path}",
        )

    template_content = template_path.read_text()

    # Build values dictionary
    values = {
        "DATE_FULL": get_date_full(timezone),
        "TIME": get_time_string(timezone),
        "LOCATION": location,
        "GTD_TASKS": gtd_tasks or "_No GTD tasks available_",
    }

    # Add any extra values
    if extra_values:
        values.update(extra_values)

    # Fill template
    content, filled, remaining = fill_template(template_content, values)

    if dry_run:
        return GenerateResult(
            success=True,
            output_path=output_path,
            content=content,
            filled_placeholders=filled,
            remaining_placeholders=remaining,
            message=(
                f"Would write to {output_path} "
                f"({len(filled)} filled, {len(remaining)} remaining)"
            ),
        )

    # Write output
    output_path.write_text(content)

    return GenerateResult(
        success=True,
        output_path=output_path,
        content=content,
        filled_placeholders=filled,
        remaining_placeholders=remaining,
        message=f"Generated {output_path.name}",
    )
