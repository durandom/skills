"""Template rendering for code map generation using stdlib string.Template."""

from pathlib import Path
from string import Template

# Directory containing template files
TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_template(name: str) -> Template:
    """Load a template file by name.

    Args:
        name: Template filename (e.g., "MAP.md", "ARCHITECTURE.md", "domain.md")

    Returns:
        string.Template object
    """
    template_path = TEMPLATES_DIR / name
    return Template(template_path.read_text())


def render_template(name: str, **kwargs: str) -> str:
    """Load and render a template with substitutions.

    Args:
        name: Template filename
        **kwargs: Variables to substitute

    Returns:
        Rendered template string with exactly one trailing newline.
    """
    template = load_template(name)
    return template.substitute(**kwargs).rstrip() + "\n"
