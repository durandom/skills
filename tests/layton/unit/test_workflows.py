"""Unit tests for workflows module."""

import sys
from pathlib import Path

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent / "skills" / "layton"),
)

from laytonlib.workflows import (
    WORKFLOW_TEMPLATE,
    WorkflowInfo,
    add_workflow,
    list_workflows,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_valid_frontmatter(self):
        """Parses valid YAML frontmatter."""
        content = """---
name: test
description: A test workflow
triggers:
  - hello
  - hi there
---

# Body content
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test workflow"
        assert result["triggers"] == ["hello", "hi there"]

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
description: A test workflow
---

# Body
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test workflow"

    def test_frontmatter_with_list(self):
        """Parses list values correctly."""
        content = """---
name: test
triggers:
  - trigger one
  - trigger two
  - trigger three
---
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["triggers"] == ["trigger one", "trigger two", "trigger three"]


class TestListWorkflows:
    """Tests for list_workflows function."""

    def test_empty_dir(self, temp_workflows_dir):
        """Returns empty list when workflows directory is empty."""
        result = list_workflows()
        assert result == []

    def test_missing_dir(self, isolated_env):
        """Returns empty list when workflows directory doesn't exist."""
        # Remove the workflows dir created by fixture
        workflows_dir = isolated_env / ".layton" / "workflows"
        if workflows_dir.exists():
            workflows_dir.rmdir()
        result = list_workflows()
        assert result == []

    def test_multiple_workflows(self, temp_workflows_dir):
        """Lists multiple workflow files sorted by name."""
        # Create workflow files
        (temp_workflows_dir / "zebra.md").write_text(
            """---
name: zebra
description: Last workflow
triggers:
  - z
---
"""
        )
        (temp_workflows_dir / "alpha.md").write_text(
            """---
name: alpha
description: First workflow
triggers:
  - a
---
"""
        )

        result = list_workflows()
        assert len(result) == 2
        assert result[0].name == "alpha"
        assert result[1].name == "zebra"

    def test_ignores_gitkeep(self, temp_workflows_dir):
        """Ignores .gitkeep file."""
        (temp_workflows_dir / ".gitkeep").touch()
        result = list_workflows()
        assert result == []

    def test_skips_invalid_files(self, temp_workflows_dir):
        """Skips files without valid frontmatter."""
        (temp_workflows_dir / "invalid.md").write_text("No frontmatter here")
        (temp_workflows_dir / "valid.md").write_text(
            """---
name: valid
description: Valid workflow
triggers:
  - test
---
"""
        )

        result = list_workflows()
        assert len(result) == 1
        assert result[0].name == "valid"


class TestAddWorkflow:
    """Tests for add_workflow function."""

    def test_creates_file(self, temp_workflows_dir):
        """Creates workflow file from template."""
        path = add_workflow("newworkflow")

        assert path.exists()
        assert path.name == "newworkflow.md"
        content = path.read_text()
        assert "name: newworkflow" in content

    def test_creates_directory(self, isolated_env):
        """Creates .layton/workflows/ if it doesn't exist."""
        workflows_dir = isolated_env / ".layton" / "workflows"
        if workflows_dir.exists():
            workflows_dir.rmdir()

        path = add_workflow("newworkflow")

        assert workflows_dir.exists()
        assert path.exists()

    def test_error_if_exists(self, temp_workflows_dir):
        """Raises FileExistsError if workflow file already exists."""
        (temp_workflows_dir / "existing.md").write_text("existing content")

        try:
            add_workflow("existing")
            assert False, "Should have raised FileExistsError"
        except FileExistsError as e:
            assert "already exists" in str(e)


class TestWorkflowTemplate:
    """Tests for workflow template."""

    def test_has_required_sections(self):
        """Template has required sections."""
        assert "## Objective" in WORKFLOW_TEMPLATE
        assert "## Steps" in WORKFLOW_TEMPLATE
        assert "## Context Adaptation" in WORKFLOW_TEMPLATE
        assert "## Success Criteria" in WORKFLOW_TEMPLATE

    def test_has_frontmatter_placeholders(self):
        """Template has frontmatter placeholders."""
        assert "name: {name}" in WORKFLOW_TEMPLATE
        assert "description:" in WORKFLOW_TEMPLATE
        assert "triggers:" in WORKFLOW_TEMPLATE


class TestWorkflowInfo:
    """Tests for WorkflowInfo dataclass."""

    def test_to_dict(self, tmp_path):
        """to_dict returns proper dictionary."""
        path = tmp_path / "test.md"
        workflow = WorkflowInfo(
            name="test",
            description="Test workflow",
            triggers=["hello", "hi"],
            path=path,
        )
        d = workflow.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test workflow"
        assert d["triggers"] == ["hello", "hi"]
        assert d["path"] == str(path)

    def test_to_dict_no_path(self):
        """to_dict without path."""
        workflow = WorkflowInfo(
            name="test",
            description="Test workflow",
            triggers=["hello"],
        )
        d = workflow.to_dict()

        assert d["name"] == "test"
        assert "path" not in d

    def test_default_triggers(self):
        """Default triggers is empty list."""
        workflow = WorkflowInfo(name="test", description="Test")
        assert workflow.triggers == []
