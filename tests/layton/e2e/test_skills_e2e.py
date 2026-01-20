"""E2E tests for layton skills command."""

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


class TestSkillsCommand:
    """E2E tests for layton skills."""

    def test_skills_outputs_json(self, isolated_env):
        """skills outputs valid JSON by default."""
        result = run_layton("skills", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "skills" in data["data"]

    def test_skills_empty(self, temp_skills_dir):
        """skills returns empty array when no skills."""
        result = run_layton("skills", cwd=temp_skills_dir.parent.parent)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["skills"] == []
        assert "next_steps" in data

    def test_skills_lists_skill(self, sample_skill_file):
        """skills lists skill files from .layton/skills/."""
        cwd = sample_skill_file.parent.parent.parent
        result = run_layton("skills", cwd=cwd)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["data"]["skills"]) == 1
        skill = data["data"]["skills"][0]
        assert skill["name"] == "sample"
        assert "description" in skill

    def test_skills_human_output(self, temp_skills_dir):
        """skills --human outputs human-readable format."""
        result = run_layton("skills", "--human", cwd=temp_skills_dir.parent.parent)

        # Human output should NOT be JSON
        try:
            json.loads(result.stdout)
            if result.stdout.strip():
                assert False, "Human output should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected


class TestSkillsDiscover:
    """E2E tests for layton skills --discover."""

    def test_discover_finds_skills(self, isolated_env, temp_skills_root):
        """skills --discover finds skills from skills/*/SKILL.md."""
        # Create a skill to discover
        skill_dir = temp_skills_root / "myskill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
name: myskill
description: Test skill
---
"""
        )

        result = run_layton("skills", "--discover", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "unknown" in data["data"]
        unknown_names = [s["name"] for s in data["data"]["unknown"]]
        assert "myskill" in unknown_names

    def test_discover_excludes_layton(self, isolated_env, temp_skills_root):
        """skills --discover excludes skills/layton/."""
        # Create layton skill (should be excluded)
        layton_dir = temp_skills_root / "layton"
        layton_dir.mkdir()
        (layton_dir / "SKILL.md").write_text(
            """---
name: layton
description: Should be excluded
---
"""
        )

        result = run_layton("skills", "--discover", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        unknown_names = [s["name"] for s in data["data"]["unknown"]]
        known_names = [s["name"] for s in data["data"]["known"]]
        assert "layton" not in unknown_names
        assert "layton" not in known_names


class TestSkillsAdd:
    """E2E tests for layton skills add."""

    def test_add_creates_file(self, isolated_env):
        """skills add creates skill file."""
        result = run_layton("skills", "add", "newskill", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "newskill" in data["data"]["created"]

        # Verify file exists
        skill_path = isolated_env / ".layton" / "skills" / "newskill.md"
        assert skill_path.exists()

    def test_add_creates_directory(self, isolated_env):
        """skills add creates .layton/skills/ if missing."""
        skills_dir = isolated_env / ".layton" / "skills"
        if skills_dir.exists():
            skills_dir.rmdir()

        result = run_layton("skills", "add", "newskill", cwd=isolated_env)

        assert result.returncode == 0
        assert skills_dir.exists()

    def test_add_error_if_exists(self, sample_skill_file):
        """skills add returns error if skill file exists."""
        cwd = sample_skill_file.parent.parent.parent
        result = run_layton("skills", "add", "sample", cwd=cwd)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "SKILL_EXISTS"
