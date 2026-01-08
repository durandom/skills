# Recipe: Skill Configuration Patterns

**Target Audience:** AI Coding Agents and skill authors
**Goal:** Design configuration systems that separate shareable behavior from person-specific paths.

---

## The Problem

Skills often need configuration: where to store data, which features to enable, API endpoints, etc. A naive approach puts everything in one config file:

```toml
# .skill.toml — DON'T DO THIS
skill_root = "/home/alice/Documents/MySkill"  # Person-specific!
sync_enabled = true                            # Shareable
api_token = "sk-abc123"                        # Secret!
```

This creates three problems:

1. **Uncommittable paths:** `/home/alice/...` breaks for other users
2. **Leaked secrets:** API tokens in repos are a security incident
3. **Fork friction:** Every contributor must edit config before using

---

## The Solution: Configuration Layers

Separate configuration into distinct layers based on what can be shared:

| Layer | Location | Contents | Commit? |
|-------|----------|----------|---------|
| **Behavior** | `.skill/config.toml` in repo | Feature flags, templates, conventions | Yes |
| **Personal** | `~/.config/<skill>/config.toml` | Filesystem paths, preferences | Never |
| **Secrets** | Environment variables or keyring | API tokens, credentials | Never |
| **Override** | `SKILL_*` environment variables | CI, testing, automation | N/A |

---

## Layer 1: Behavior Configuration (Committable)

Settings that define *how* the skill behaves, independent of *where* it runs.

**Location:** `.skill/config.toml` or `.<skillname>.toml` in repo root

**What belongs here:**

- Feature flags and toggles
- Naming conventions
- Template choices
- Integration settings (enable/disable)
- Default values for optional parameters

```toml
# .para/config.toml — COMMIT THIS

[behavior]
sync_with_gtd = true
folder_prefix = true          # "1 Projects" vs "Projects"
naming_convention = "kebab-case"

[templates]
project = "project-v2"
area = "area-standard"

[integrations]
gtd = { enabled = true, create_milestones = true }
obsidian = { enabled = false }
```

**What does NOT belong here:**

- Absolute filesystem paths (`/home/...`, `C:\Users\...`)
- Usernames, email addresses
- API tokens, passwords
- Personal preferences (editor, theme)

---

## Layer 2: Personal Configuration (Never Commit)

Settings that vary per person: where their files live, their preferences.

**Location:** `~/.config/<skill>/config.toml` (XDG Base Directory spec)

**Fallback locations:**

- Linux/macOS: `~/.config/<skill>/config.toml`
- macOS alternative: `~/Library/Application Support/<skill>/config.toml`
- Windows: `%APPDATA%\<skill>\config.toml`

```toml
# ~/.config/para/config.toml — NEVER COMMIT

# Global default root
para_root = "/home/alice/Documents/PARA"

# Per-repo overrides (longest prefix match)
[repos]
"/home/alice/work/project-alpha" = "/home/alice/Notes/work-alpha"
"/home/alice/work" = "/home/alice/Notes/work"
"/home/alice/personal" = "/home/alice/Notes/personal"
```

**Resolution for repo mappings:**

```python
def find_repo_mapping(git_root: Path, repos: dict) -> Path | None:
    """Find longest prefix match for git repo."""
    git_root_str = str(git_root)
    best_match = None
    best_len = 0

    for repo_path, skill_root in repos.items():
        repo_expanded = str(Path(repo_path).expanduser())
        if git_root_str.startswith(repo_expanded):
            if len(repo_expanded) > best_len:
                best_match = skill_root
                best_len = len(repo_expanded)

    return Path(best_match) if best_match else None
```

---

## Layer 3: Secrets (Never Commit, Never Log)

API tokens, passwords, and credentials.

**Location options (in precedence order):**

1. **Environment variables** (recommended for CI)

   ```bash
   export SKILL_API_TOKEN="your-token-here"
   ```

2. **System keyring** (recommended for interactive use)

   ```python
   import keyring
   token = keyring.get_password("skill-name", "api-token")
   ```

3. **Separate secrets file** (if needed)

   ```toml
   # ~/.config/skill/secrets.toml — mode 600, NEVER COMMIT
   api_token = "your-token-here"
   ```

**Never:**

- Put secrets in behavior config (`.skill/config.toml`)
- Log secrets in verbose output
- Include secrets in error messages

---

## Layer 4: Environment Overrides

For CI, testing, and automation. Environment variables override all other layers.

**Naming convention:** `<SKILL>_<SETTING>` in SCREAMING_SNAKE_CASE

```bash
# Override root for CI
export PARA_ROOT="/tmp/test-para"

# Override behavior for testing
export PARA_SYNC_ENABLED="false"

# Run skill
para status
```

**Implementation:**

```python
import os

def get_config_value(key: str, default=None):
    """Get config with environment override."""
    env_key = f"SKILL_{key.upper()}"

    # 1. Environment override (highest priority)
    if env_value := os.environ.get(env_key):
        return parse_env_value(env_value)

    # 2. User config
    user_config = load_user_config()
    if key in user_config:
        return user_config[key]

    # 3. Behavior config
    behavior_config = load_behavior_config()
    if key in behavior_config:
        return behavior_config[key]

    # 4. Default
    return default
```

---

## Complete Resolution Order

When resolving a configuration value, check layers in this order:

```
1. Environment variable     SKILL_ROOT="/tmp/test"
         ↓ (if not set)
2. User config              ~/.config/skill/config.toml
         ↓ (if not set)
3. Repo mapping             [repos] section, longest prefix match
         ↓ (if not set)
4. Behavior config          .skill/config.toml in repo
         ↓ (if not set)
5. Auto-discovery           Walk up from cwd looking for markers
         ↓ (if not found)
6. Error with guidance      "Run: skill config --set-root /path"
```

---

## Implementation Example

```python
#!/usr/bin/env python3
"""Skill configuration with proper layer separation."""

import os
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Python < 3.11

# XDG-compliant config location
def get_config_dir(skill_name: str) -> Path:
    """Get XDG config directory for skill."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    return Path(xdg_config).expanduser() / skill_name


def load_user_config(skill_name: str) -> dict:
    """Load user's personal config (paths, preferences)."""
    config_file = get_config_dir(skill_name) / "config.toml"
    if not config_file.exists():
        return {}
    return tomllib.loads(config_file.read_text())


def load_behavior_config(skill_name: str) -> dict:
    """Load repo's behavior config (feature flags, templates)."""
    # Look for .skill/config.toml or .skillname.toml
    cwd = Path.cwd()
    candidates = [
        cwd / f".{skill_name}" / "config.toml",
        cwd / f".{skill_name}.toml",
    ]

    for candidate in candidates:
        if candidate.exists():
            return tomllib.loads(candidate.read_text())

    return {}


def find_git_root() -> Path | None:
    """Find the root of the current git repository."""
    cwd = Path.cwd()
    for path in [cwd] + list(cwd.parents):
        if (path / ".git").exists():
            return path
    return None


def resolve_skill_root(skill_name: str, marker_folders: list[str]) -> Path | None:
    """Resolve skill root with proper layer precedence.

    Args:
        skill_name: Name of the skill (for config lookup)
        marker_folders: Folders that indicate a skill root (for auto-discovery)

    Returns:
        Resolved path or None if not found
    """
    env_var = f"{skill_name.upper()}_ROOT"

    # 1. Environment override
    if env_root := os.environ.get(env_var):
        path = Path(env_root).expanduser()
        if path.exists():
            return path

    user_config = load_user_config(skill_name)

    # 2. Repo mapping (longest prefix match)
    git_root = find_git_root()
    if git_root and "repos" in user_config:
        repos = user_config["repos"]
        git_str = str(git_root)
        best_match, best_len = None, 0

        for repo_path, skill_root in repos.items():
            repo_expanded = str(Path(repo_path).expanduser())
            if git_str.startswith(repo_expanded) and len(repo_expanded) > best_len:
                best_match = skill_root
                best_len = len(repo_expanded)

        if best_match:
            path = Path(best_match).expanduser()
            if path.exists():
                return path

    # 3. User config default
    if default_root := user_config.get(f"{skill_name}_root"):
        path = Path(default_root).expanduser()
        if path.exists():
            return path

    # 4. Auto-discovery (walk up from cwd)
    cwd = Path.cwd()
    for path in [cwd] + list(cwd.parents):
        for marker in marker_folders:
            if (path / marker).exists():
                return path

    return None


def get_feature_flag(skill_name: str, flag: str, default: bool = False) -> bool:
    """Get a feature flag with environment override."""
    env_var = f"{skill_name.upper()}_{flag.upper()}"

    # Environment override
    if env_value := os.environ.get(env_var):
        return env_value.lower() in ("true", "1", "yes")

    # Behavior config
    behavior = load_behavior_config(skill_name)
    return behavior.get("behavior", {}).get(flag, default)
```

---

## CLI Commands for Configuration

Follow the [Agentic CLI patterns](agentic-cli.md) for config management:

```
$ skill config
Config file: ~/.config/skill/config.toml

Default:
  skill_root = /home/alice/Documents/Skill

Repo mappings:
  /home/alice/work/project-a
    → /home/alice/Notes/work

Current context:
  Git repo: /home/alice/work/project-a
  Behavior config: .skill/config.toml (found)

Effective root: /home/alice/Notes/work

Next steps:
  skill config --set-root PATH    Set default root
  skill config --set-repo . PATH  Map current repo
  skill init --path PATH          Initialize new root
```

**Key flags:**

```
--set-root PATH       Set global default (personal config)
--unset-root          Remove global default
--set-repo REPO PATH  Map git repo to skill root
--unset-repo REPO     Remove repo mapping
--show-behavior       Show behavior config from repo
```

---

## Anti-Patterns

### Don't mix layers in one file

```toml
# BAD: .skill.toml in repo (mixes layers)
skill_root = "/home/alice/Documents"  # Person-specific! Don't commit!
sync_enabled = true                    # Shareable - OK to commit
```

### Don't use interactive prompts for paths

```python
# BAD: Blocks agents
path = input("Enter skill root: ")

# GOOD: Clear error with next steps
print("Error: Skill root not configured.")
print("  Run: skill config --set-root /path/to/root")
sys.exit(1)
```

### Don't auto-create in home directory

```python
# BAD: Creates files without consent
default_root = Path.home() / "Skill"
default_root.mkdir(exist_ok=True)

# GOOD: Require explicit initialization
if not root:
    print("Run: skill init --path /desired/location")
    sys.exit(1)
```

### Don't store secrets in config files

```toml
# BAD: secrets.toml or config.toml
api_token = "never-commit-real-tokens"

# GOOD: Environment variable
# export SKILL_API_TOKEN="your-token-here"
```

---

## Checklist for Skill Authors

- [ ] Behavior config (`.skill/config.toml`) contains NO paths
- [ ] Personal config uses XDG location (`~/.config/skill/`)
- [ ] Environment variables can override any setting
- [ ] `skill config` shows current resolution clearly
- [ ] Missing config shows actionable error, not interactive prompt
- [ ] Secrets use environment variables or keyring
- [ ] Repo mappings use longest prefix match
- [ ] Auto-discovery is the fallback, not the primary method

---

## References

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [Agentic CLI Design Patterns](agentic-cli.md)
- [12-Factor App: Config](https://12factor.net/config)
