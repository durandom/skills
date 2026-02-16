"""Tests for GTD configuration loading and saving."""

import json

from gtdlib.config import (
    GitHubConfig,
    GTDConfig,
    TaskwarriorConfig,
    load_config,
    save_config,
)


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
