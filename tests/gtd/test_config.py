"""Tests for GTD configuration loading and saving."""

import json
from pathlib import Path

from gtdlib.config import (
    GitHubConfig,
    GTDConfig,
    TaskwarriorConfig,
    detect_skill_directory,
    load_config,
    save_config,
)


class TestScriptPathResolution:
    """Verify the gtd script uses __file__ to set up sys.path."""

    def test_gtd_script_has_explicit_path_setup(self):
        """The gtd script must use __file__ to set up sys.path."""
        script = Path(__file__).parent.parent.parent / "skills/gtd/scripts/gtd"
        content = script.read_text()
        assert "__file__" in content
        assert "sys.path" in content


class TestWrongDirectoryDetection:
    """Test detect_skill_directory() from Pattern 3."""

    def test_detect_skill_directory_positive(self, tmp_path):
        """Detects when cwd is the skill directory."""
        (tmp_path / "SKILL.md").touch()
        (tmp_path / "scripts").mkdir()
        assert detect_skill_directory(tmp_path) is True

    def test_detect_skill_directory_negative(self, tmp_path):
        """Normal project directory is not detected."""
        (tmp_path / ".gtd").mkdir()
        assert detect_skill_directory(tmp_path) is False

    def test_detect_skill_directory_partial(self, tmp_path):
        """Directory with only SKILL.md is not detected (needs both)."""
        (tmp_path / "SKILL.md").touch()
        assert detect_skill_directory(tmp_path) is False


class TestLoadConfig:
    """Test configuration loading from files."""

    def test_load_missing_file_returns_defaults(self, tmp_path):
        config = load_config(tmp_path / "nonexistent.json")
        assert config.backend == "github"

    def test_load_valid_taskwarrior_config(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"backend": "taskwarrior"}))
        config = load_config(config_file)
        assert config.backend == "taskwarrior"

    def test_load_invalid_json_returns_defaults(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text("not json at all")
        config = load_config(config_file)
        assert config.backend == "github"

    def test_load_unknown_backend_falls_back_to_github(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"backend": "nosql_yolo"}))
        config = load_config(config_file)
        assert config.backend == "github"

    def test_load_taskwarrior_with_custom_data_dir(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {"backend": "taskwarrior", "taskwarrior": {"data_dir": "/custom/path"}}
            )
        )
        config = load_config(config_file)
        assert config.taskwarrior.data_dir == "/custom/path"

    def test_load_github_with_repo(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"backend": "github", "github": {"repo": "owner/repo"}})
        )
        config = load_config(config_file)
        assert config.github.repo == "owner/repo"

    def test_load_corrupt_backend_section_uses_defaults(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"backend": "taskwarrior", "taskwarrior": "not a dict"})
        )
        config = load_config(config_file)
        assert config.taskwarrior.data_dir == ".gtd/taskwarrior"


class TestSaveConfig:
    """Test configuration saving."""

    def test_save_minimal_github_config(self, tmp_path):
        path = tmp_path / "config.json"
        config = GTDConfig(backend="github")
        save_config(config, path)
        data = json.loads(path.read_text())
        assert data == {"backend": "github"}

    def test_save_taskwarrior_with_default_dir_omits_section(self, tmp_path):
        path = tmp_path / "config.json"
        config = GTDConfig(backend="taskwarrior")
        save_config(config, path)
        data = json.loads(path.read_text())
        assert data == {"backend": "taskwarrior"}
        assert "taskwarrior" not in data  # default is omitted

    def test_save_taskwarrior_with_custom_dir_includes_section(self, tmp_path):
        path = tmp_path / "config.json"
        config = GTDConfig(
            backend="taskwarrior",
            taskwarrior=TaskwarriorConfig(data_dir="/custom"),
        )
        save_config(config, path)
        data = json.loads(path.read_text())
        assert data["taskwarrior"]["data_dir"] == "/custom"

    def test_save_github_with_repo_includes_section(self, tmp_path):
        path = tmp_path / "config.json"
        config = GTDConfig(backend="github", github=GitHubConfig(repo="me/myrepo"))
        save_config(config, path)
        data = json.loads(path.read_text())
        assert data["github"]["repo"] == "me/myrepo"

    def test_roundtrip_config(self, tmp_path):
        path = tmp_path / "config.json"
        original = GTDConfig(
            backend="taskwarrior",
            taskwarrior=TaskwarriorConfig(data_dir="/my/data"),
        )
        save_config(original, path)
        loaded = load_config(path)
        assert loaded.backend == "taskwarrior"
        assert loaded.taskwarrior.data_dir == "/my/data"
