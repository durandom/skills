"""E2E tests for layton workflows command."""

import json
import subprocess
import sys
from pathlib import Path


def run_layton(*args, cwd=None):
    """Run layton CLI and return result."""
    script_path = (
        Path(__file__).parent.parent.parent.parent
        / "skills"
        / "layton"
        / "scripts"
        / "layton"
    )
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result


class TestWorkflowsCommand:
    """E2E tests for layton workflows."""

    def test_workflows_outputs_json(self, isolated_env):
        """workflows outputs valid JSON by default."""
        result = run_layton("workflows", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "workflows" in data["data"]

    def test_workflows_empty(self, temp_workflows_dir):
        """workflows returns empty array when no workflows."""
        result = run_layton("workflows", cwd=temp_workflows_dir.parent.parent)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["workflows"] == []
        assert "next_steps" in data

    def test_workflows_lists_workflow(self, sample_workflow_file):
        """workflows lists workflow files from .layton/workflows/."""
        cwd = sample_workflow_file.parent.parent.parent
        result = run_layton("workflows", cwd=cwd)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["data"]["workflows"]) == 1
        workflow = data["data"]["workflows"][0]
        assert workflow["name"] == "sample"
        assert "description" in workflow
        assert "triggers" in workflow

    def test_workflows_human_output(self, temp_workflows_dir):
        """workflows --human outputs human-readable format."""
        result = run_layton(
            "workflows", "--human", cwd=temp_workflows_dir.parent.parent
        )

        # Human output should NOT be JSON
        try:
            json.loads(result.stdout)
            if result.stdout.strip():
                assert False, "Human output should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected


class TestWorkflowsAdd:
    """E2E tests for layton workflows add."""

    def test_add_creates_file(self, isolated_env):
        """workflows add creates workflow file."""
        result = run_layton("workflows", "add", "newworkflow", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "newworkflow" in data["data"]["created"]

        # Verify file exists
        workflow_path = isolated_env / ".layton" / "workflows" / "newworkflow.md"
        assert workflow_path.exists()

    def test_add_creates_directory(self, isolated_env):
        """workflows add creates .layton/workflows/ if missing."""
        workflows_dir = isolated_env / ".layton" / "workflows"
        if workflows_dir.exists():
            workflows_dir.rmdir()

        result = run_layton("workflows", "add", "newworkflow", cwd=isolated_env)

        assert result.returncode == 0
        assert workflows_dir.exists()

    def test_add_error_if_exists(self, sample_workflow_file):
        """workflows add returns error if workflow file exists."""
        cwd = sample_workflow_file.parent.parent.parent
        result = run_layton("workflows", "add", "sample", cwd=cwd)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "WORKFLOW_EXISTS"

    def test_add_template_has_required_sections(self, isolated_env):
        """workflows add creates file with required sections."""
        run_layton("workflows", "add", "testworkflow", cwd=isolated_env)

        workflow_path = isolated_env / ".layton" / "workflows" / "testworkflow.md"
        content = workflow_path.read_text()

        assert "## Objective" in content
        assert "## Steps" in content
        assert "## Context Adaptation" in content
        assert "## Success Criteria" in content
