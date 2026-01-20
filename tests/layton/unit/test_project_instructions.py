"""Unit tests for project instructions documentation."""

from pathlib import Path

# Path to the Layton skill directory
LAYTON_SKILL_DIR = Path(__file__).parent.parent.parent.parent / "skills" / "layton"


class TestReferenceDocument:
    """Tests for references/project-instructions.md."""

    def test_reference_doc_exists(self):
        """Reference document exists at expected path."""
        ref_path = LAYTON_SKILL_DIR / "references" / "project-instructions.md"
        assert ref_path.exists(), f"Missing reference doc at {ref_path}"

    def test_reference_covers_claude_md(self):
        """Reference document covers CLAUDE.md purpose and guidance."""
        ref_path = LAYTON_SKILL_DIR / "references" / "project-instructions.md"
        content = ref_path.read_text().lower()

        # Check for CLAUDE.md coverage
        assert "claude.md" in content, "Reference should mention CLAUDE.md"
        assert "@agents.md" in content, (
            "Reference should explain CLAUDE.md includes @AGENTS.md"
        )

    def test_reference_covers_agents_md(self):
        """Reference document covers AGENTS.md purpose and guidance."""
        ref_path = LAYTON_SKILL_DIR / "references" / "project-instructions.md"
        content = ref_path.read_text().lower()

        # Check for AGENTS.md coverage
        assert "agents.md" in content, "Reference should mention AGENTS.md"
        assert "session" in content, "Reference should mention session protocols"
        assert "critical" in content or "rules" in content, (
            "Reference should mention critical rules"
        )

    def test_reference_includes_antipatterns(self):
        """Reference document includes anti-patterns section."""
        ref_path = LAYTON_SKILL_DIR / "references" / "project-instructions.md"
        content = ref_path.read_text().lower()

        # Check for anti-patterns
        assert "anti-pattern" in content or "antipattern" in content, (
            "Reference should have anti-patterns section"
        )
        assert "duplication" in content or "duplicate" in content, (
            "Reference should warn against duplication"
        )


class TestExampleClaudeMd:
    """Tests for examples/CLAUDE.md."""

    def test_example_claude_md_exists(self):
        """Example CLAUDE.md exists at expected path."""
        example_path = LAYTON_SKILL_DIR / "examples" / "CLAUDE.md"
        assert example_path.exists(), f"Missing example at {example_path}"

    def test_example_claude_md_includes_agents(self):
        """Example CLAUDE.md includes @AGENTS.md directive."""
        example_path = LAYTON_SKILL_DIR / "examples" / "CLAUDE.md"
        content = example_path.read_text()

        assert "@AGENTS.md" in content or "@agents.md" in content.lower(), (
            "Example CLAUDE.md should include @AGENTS.md"
        )

    def test_example_claude_md_minimal(self):
        """Example CLAUDE.md is minimal (under 10 lines)."""
        example_path = LAYTON_SKILL_DIR / "examples" / "CLAUDE.md"
        content = example_path.read_text()
        line_count = len(content.strip().split("\n"))

        assert line_count <= 10, (
            f"Example CLAUDE.md should be minimal (under 10 lines), got {line_count}"
        )


class TestExampleAgentsMd:
    """Tests for examples/AGENTS.md."""

    def test_example_agents_md_exists(self):
        """Example AGENTS.md exists at expected path."""
        example_path = LAYTON_SKILL_DIR / "examples" / "AGENTS.md"
        assert example_path.exists(), f"Missing example at {example_path}"

    def test_example_agents_md_sections(self):
        """Example AGENTS.md has required sections."""
        example_path = LAYTON_SKILL_DIR / "examples" / "AGENTS.md"
        content = example_path.read_text()
        content_lower = content.lower()

        # Check for required sections
        assert "mandatory" in content_lower or "session start" in content_lower, (
            "Example should have session start protocol"
        )
        assert "entry point" in content_lower or "layton" in content_lower, (
            "Example should mention Layton as entry point"
        )
        assert "session" in content_lower and "completion" in content_lower, (
            "Example should have session completion section"
        )
        assert "critical" in content_lower and "rules" in content_lower, (
            "Example should have critical rules"
        )

    def test_example_agents_md_has_commands(self):
        """Example AGENTS.md has Beads commands."""
        example_path = LAYTON_SKILL_DIR / "examples" / "AGENTS.md"
        content = example_path.read_text()

        assert "bd ready" in content or "bd show" in content, (
            "Example should have Beads commands"
        )

    def test_example_agents_md_concise(self):
        """Example AGENTS.md is concise (under 60 lines)."""
        example_path = LAYTON_SKILL_DIR / "examples" / "AGENTS.md"
        content = example_path.read_text()
        line_count = len(content.strip().split("\n"))

        assert line_count <= 60, (
            f"Example AGENTS.md should be under 60 lines, got {line_count}"
        )
