"""Tests for PARA CLI functions."""

import tomllib

import pytest


class TestDetectSkillDirectory:
    """Test detect_skill_directory() — Pattern 3."""

    def test_detect_skill_directory_positive(self, para, tmp_path):
        """Detects when cwd is the skill directory."""
        (tmp_path / "SKILL.md").touch()
        (tmp_path / "scripts").mkdir()
        assert para.detect_skill_directory(tmp_path) is True

    def test_detect_skill_directory_negative(self, para, tmp_path):
        """Normal directory is not detected."""
        assert para.detect_skill_directory(tmp_path) is False

    def test_detect_skill_directory_partial(self, para, tmp_path):
        """Directory with only SKILL.md is not a skill directory."""
        (tmp_path / "SKILL.md").touch()
        assert para.detect_skill_directory(tmp_path) is False


class TestFindGitRoot:
    """Test find_git_root()."""

    def test_finds_git_root(self, para, tmp_path, monkeypatch):
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)
        assert para.find_git_root() == tmp_path

    def test_finds_git_root_from_subdirectory(self, para, tmp_path, monkeypatch):
        (tmp_path / ".git").mkdir()
        sub = tmp_path / "a" / "b"
        sub.mkdir(parents=True)
        monkeypatch.chdir(sub)
        assert para.find_git_root() == tmp_path

    def test_returns_none_outside_git(self, para, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert para.find_git_root() is None


class TestLoadConfig:
    """Test load_config() — global config loading."""

    def test_returns_empty_dict_when_missing(self, para, tmp_path, monkeypatch):
        monkeypatch.setattr(para, "CONFIG_FILE", tmp_path / "nonexistent.toml")
        assert para.load_config() == {}

    def test_loads_toml_config(self, para, tmp_path, monkeypatch):
        config_file = tmp_path / "config.toml"
        config_file.write_text('para_root = "/home/user/notes"\n')
        monkeypatch.setattr(para, "CONFIG_FILE", config_file)
        config = para.load_config()
        assert config["para_root"] == "/home/user/notes"

    def test_loads_config_with_repos_section(self, para, tmp_path, monkeypatch):
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            'para_root = "/default"\n\n[repos]\n"/repo/a" = "/para/a"\n'
        )
        monkeypatch.setattr(para, "CONFIG_FILE", config_file)
        config = para.load_config()
        assert config["para_root"] == "/default"
        assert config["repos"]["/repo/a"] == "/para/a"


class TestLoadLocalConfig:
    """Test load_local_config() — per-repo .para.toml."""

    def test_returns_empty_dict_when_missing(self, para, tmp_path):
        assert para.load_local_config(tmp_path) == {}

    def test_loads_para_toml(self, para, tmp_path):
        (tmp_path / ".para.toml").write_text('para_root = "/my/notes"\n')
        config = para.load_local_config(tmp_path)
        assert config["para_root"] == "/my/notes"

    def test_raises_on_malformed_toml(self, para, tmp_path):
        """Malformed TOML raises TOMLDecodeError (tomllib is strict)."""
        (tmp_path / ".para.toml").write_text("# comment\nbadline\n")
        with pytest.raises(tomllib.TOMLDecodeError):
            para.load_local_config(tmp_path)


class TestFindParaRoot:
    """Test find_para_root() — 4-tier resolution."""

    def test_returns_none_when_no_config(self, para, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(para, "CONFIG_FILE", tmp_path / "nonexistent.toml")
        assert para.find_para_root() is None

    def test_finds_para_by_folder_markers(self, para, tmp_path, monkeypatch):
        (tmp_path / "1_Projects").mkdir()
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(para, "CONFIG_FILE", tmp_path / "nonexistent.toml")
        assert para.find_para_root() == tmp_path

    def test_finds_para_by_areas_folder(self, para, tmp_path, monkeypatch):
        (tmp_path / "2_Areas").mkdir()
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(para, "CONFIG_FILE", tmp_path / "nonexistent.toml")
        assert para.find_para_root() == tmp_path

    def test_global_config_para_root(self, para, tmp_path, monkeypatch):
        para_dir = tmp_path / "para"
        para_dir.mkdir()
        config_file = tmp_path / "config.toml"
        config_file.write_text(f'para_root = "{para_dir}"\n')
        monkeypatch.setattr(para, "CONFIG_FILE", config_file)
        monkeypatch.chdir(tmp_path)
        assert para.find_para_root() == para_dir

    def test_local_para_toml_takes_priority(self, para, tmp_path, monkeypatch):
        """Local .para.toml should override global config."""
        # Set up git root
        (tmp_path / ".git").mkdir()
        # Local config points to local_para
        local_para = tmp_path / "local_para"
        local_para.mkdir()
        (tmp_path / ".para.toml").write_text(f'para_root = "{local_para}"\n')
        # Global config points elsewhere
        global_para = tmp_path / "global_para"
        global_para.mkdir()
        config_file = tmp_path / "global_config.toml"
        config_file.write_text(f'para_root = "{global_para}"\n')
        monkeypatch.setattr(para, "CONFIG_FILE", config_file)
        monkeypatch.chdir(tmp_path)
        assert para.find_para_root() == local_para


class TestValidateProjectName:
    """Test _validate_project_name()."""

    def test_valid_name(self, para):
        assert para._validate_project_name("My-Project") is None

    def test_rejects_path_separator(self, para):
        assert para._validate_project_name("foo/bar") is not None

    def test_rejects_dotdot(self, para):
        assert para._validate_project_name("..") is not None

    def test_rejects_dotdot_prefix(self, para):
        assert para._validate_project_name("../etc") is not None


class TestParaFolders:
    """Test PARA_FOLDERS constants."""

    def test_para_folders_correct(self, para):
        assert para.PARA_FOLDERS == {
            "projects": "1_Projects",
            "areas": "2_Areas",
            "resources": "3_Resources",
            "archive": "4_Archive",
        }


class TestBootstrapCommands:
    """Test Pattern 4 — config is a bootstrap command."""

    def test_config_does_not_call_get_para_root(self, para):
        """cmd_config should load config directly, not via get_para_root()."""
        import inspect

        source = inspect.getsource(para.cmd_config)
        assert "get_para_root" not in source
