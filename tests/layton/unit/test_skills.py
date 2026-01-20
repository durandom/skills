"""Unit tests for skills module."""

import sys
from pathlib import Path

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent / "skills" / "layton"),
)

from laytonlib.skills import (
    SKILL_TEMPLATE,
    DiscoveredSkill,
    SkillInfo,
    add_skill,
    discover_skills,
    list_skills,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_valid_frontmatter(self):
        """Parses valid YAML frontmatter."""
        content = """---
name: test
description: A test skill
source: skills/test/SKILL.md
---

# Body content
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test skill"
        assert result["source"] == "skills/test/SKILL.md"

    def test_no_frontmatter(self):
        """Returns None for content without frontmatter."""
        content = "# Just a header\n\nSome content."
        result = parse_frontmatter(content)
        assert result is None

    def test_empty_frontmatter(self):
        """Returns None for empty frontmatter."""
        content = """---
---

# Body content
"""
        result = parse_frontmatter(content)
        assert result is None

    def test_frontmatter_with_comments(self):
        """Skips comment lines in frontmatter."""
        content = """---
name: test
# This is a comment
description: A test skill
---

# Body
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test skill"


class TestListSkills:
    """Tests for list_skills function."""

    def test_empty_dir(self, temp_skills_dir):
        """Returns empty list when skills directory is empty."""
        result = list_skills()
        assert result == []

    def test_missing_dir(self, isolated_env):
        """Returns empty list when skills directory doesn't exist."""
        # Remove the skills dir created by fixture
        skills_dir = isolated_env / ".layton" / "skills"
        if skills_dir.exists():
            skills_dir.rmdir()
        result = list_skills()
        assert result == []

    def test_multiple_skills(self, temp_skills_dir):
        """Lists multiple skill files sorted by name."""
        # Create skill files
        (temp_skills_dir / "zebra.md").write_text(
            """---
name: zebra
description: Last skill
source: skills/zebra/SKILL.md
---
"""
        )
        (temp_skills_dir / "alpha.md").write_text(
            """---
name: alpha
description: First skill
source: skills/alpha/SKILL.md
---
"""
        )

        result = list_skills()
        assert len(result) == 2
        assert result[0].name == "alpha"
        assert result[1].name == "zebra"

    def test_ignores_gitkeep(self, temp_skills_dir):
        """Ignores .gitkeep file."""
        (temp_skills_dir / ".gitkeep").touch()
        result = list_skills()
        assert result == []

    def test_skips_invalid_files(self, temp_skills_dir):
        """Skips files without valid frontmatter."""
        (temp_skills_dir / "invalid.md").write_text("No frontmatter here")
        (temp_skills_dir / "valid.md").write_text(
            """---
name: valid
description: Valid skill
source: skills/valid/SKILL.md
---
"""
        )

        result = list_skills()
        assert len(result) == 1
        assert result[0].name == "valid"


class TestDiscoverSkills:
    """Tests for discover_skills function."""

    def test_finds_skills(self, isolated_env, temp_skills_root):
        """Discovers skills from skills/*/SKILL.md."""
        # Create a skill directory with SKILL.md
        skill_dir = temp_skills_root / "myskill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
name: myskill
description: My test skill
---
"""
        )

        known, unknown = discover_skills()
        assert len(unknown) == 1
        assert unknown[0].name == "myskill"
        assert unknown[0].description == "My test skill"

    def test_excludes_layton(self, isolated_env, temp_skills_root):
        """Excludes skills/layton/ from discovery."""
        # Create layton directory
        layton_dir = temp_skills_root / "layton"
        layton_dir.mkdir()
        (layton_dir / "SKILL.md").write_text(
            """---
name: layton
description: Should be excluded
---
"""
        )

        known, unknown = discover_skills()
        assert not any(s.name == "layton" for s in unknown)
        assert not any(s.name == "layton" for s in known)

    def test_known_vs_unknown(self, isolated_env, temp_skills_root, temp_skills_dir):
        """Separates known (with skill file) from unknown skills."""
        # Create discovered skill
        skill_dir = temp_skills_root / "discovered"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
name: discovered
description: A discovered skill
---
"""
        )

        # Create known skill file
        (temp_skills_dir / "discovered.md").write_text(
            """---
name: discovered
description: A discovered skill
source: skills/discovered/SKILL.md
---
"""
        )

        known, unknown = discover_skills()
        assert len(known) == 1
        assert known[0].name == "discovered"
        assert len(unknown) == 0


class TestAddSkill:
    """Tests for add_skill function."""

    def test_creates_file(self, temp_skills_dir):
        """Creates skill file from template."""
        path = add_skill("newskill")

        assert path.exists()
        assert path.name == "newskill.md"
        content = path.read_text()
        assert "name: newskill" in content

    def test_creates_directory(self, isolated_env):
        """Creates .layton/skills/ if it doesn't exist."""
        skills_dir = isolated_env / ".layton" / "skills"
        if skills_dir.exists():
            skills_dir.rmdir()

        path = add_skill("newskill")

        assert skills_dir.exists()
        assert path.exists()

    def test_error_if_exists(self, temp_skills_dir):
        """Raises FileExistsError if skill file already exists."""
        (temp_skills_dir / "existing.md").write_text("existing content")

        try:
            add_skill("existing")
            assert False, "Should have raised FileExistsError"
        except FileExistsError as e:
            assert "already exists" in str(e)


class TestSkillTemplate:
    """Tests for skill template."""

    def test_has_required_sections(self):
        """Template has required sections."""
        assert "## Commands" in SKILL_TEMPLATE
        assert "## What to Extract" in SKILL_TEMPLATE
        assert "## Key Metrics" in SKILL_TEMPLATE

    def test_has_frontmatter_placeholders(self):
        """Template has frontmatter placeholders."""
        assert "name: {name}" in SKILL_TEMPLATE
        assert "description:" in SKILL_TEMPLATE
        assert "source:" in SKILL_TEMPLATE


class TestSkillInfo:
    """Tests for SkillInfo dataclass."""

    def test_to_dict(self, tmp_path):
        """to_dict returns proper dictionary."""
        path = tmp_path / "test.md"
        skill = SkillInfo(
            name="test",
            description="Test skill",
            source="skills/test/SKILL.md",
            path=path,
        )
        d = skill.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test skill"
        assert d["source"] == "skills/test/SKILL.md"
        assert d["path"] == str(path)


class TestDiscoveredSkill:
    """Tests for DiscoveredSkill dataclass."""

    def test_to_dict(self):
        """to_dict returns proper dictionary."""
        skill = DiscoveredSkill(
            name="test",
            description="Test skill",
            source="skills/test/SKILL.md",
        )
        d = skill.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test skill"
        assert d["source"] == "skills/test/SKILL.md"
