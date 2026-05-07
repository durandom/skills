# Recipe: CLI Location & Config Discovery for Agent Skills

**Target Audience:** AI Coding Agents building skills that bundle CLI tools
**Goal:** Ensure skill-bundled scripts can reliably find themselves and their config from any working directory.

---

## The Problem

Skills bundle CLI scripts, but those scripts run from arbitrary working directories — the project root, a plugin cache, a subdirectory, or even the skill directory itself. The script needs to find:

1. **Itself** — its own absolute path (to locate sibling modules)
2. **Its config** — a project-local config directory (like `.layton/`, `.config/`)

Neither can be hardcoded. The skill may be installed via plugin system in `~/.claude/plugin-cache/`, manually in `.claude/skills/`, or symlinked from a development directory.

---

## Pattern 1: Script Path Resolution

**Problem:** The CLI script needs to import sibling modules, but `sys.path` reflects cwd, not the script location.

**Two-part solution:**

### Part A: SKILL.md Location Hint

Tell the agent how to derive the script path from the SKILL.md path:

```markdown
The CLI script is at `scripts/my-tool` **relative to this SKILL.md file**
(not the working directory). Derive the script location from the path of
this file:

- If SKILL.md is at `/path/to/my-skill/SKILL.md`
- Then the CLI is at `/path/to/my-skill/scripts/my-tool`
```

### Part B: Python `__file__` Resolution in the Script

The script itself resolves its location using `__file__`:

```python
import sys
from pathlib import Path

# Resolve the script's actual location (follows symlinks)
script_dir = Path(__file__).parent.resolve()

# Add sibling library to import path
lib_dir = script_dir / "mylib"
sys.path.insert(0, str(lib_dir.parent))
```

**Why both?** The SKILL.md hint ensures the agent calls the right path. The `__file__` resolution ensures the script works regardless of how it was invoked.

---

## Pattern 2: Upward Config Walk

**Problem:** The script needs to find a project-local config directory (e.g., `.layton/`), but cwd could be any subdirectory of the project — or a completely unrelated directory.

**Solution:** Walk upward from cwd until you find the marker directory:

```python
from pathlib import Path


def find_vault_root(marker: str = ".layton") -> Path | None:
    """Find the nearest ancestor directory containing a config marker.

    Walks upward from cwd. Returns the directory containing the marker
    (not the marker itself), or None if not found.
    """
    current = Path.cwd().resolve()
    while True:
        if (current / marker).is_dir():
            return current
        parent = current.parent
        if parent == current:  # filesystem root
            break
        current = parent
    return None
```

**Fallback for bootstrap commands:**

```python
def get_config_dir(marker: str = ".layton") -> Path:
    """Get the config directory path.

    Uses find_vault_root() for discovery. Falls back to cwd
    (for bootstrap commands like 'config init').
    """
    vault_root = find_vault_root(marker)
    base = vault_root if vault_root else Path.cwd()
    return base / marker
```

---

## Pattern 3: Wrong-Directory Detection

**Problem:** Claude sometimes `cd`s into the skill directory before running the script. The skill directory contains a `SKILL.md` and `scripts/` but no project config — so the CLI runs but operates on nothing useful, producing confusing results.

**Solution:** Fingerprint the skill directory and emit a targeted error:

```python
from pathlib import Path


def detect_skill_directory(fingerprint: list[str] | None = None) -> bool:
    """Detect if cwd is the skill directory itself.

    Uses a unique file fingerprint. Default checks for SKILL.md + scripts/lib
    structure that only exists in the skill source, not in a project.
    """
    cwd = Path.cwd()
    if fingerprint is None:
        fingerprint = ["SKILL.md", "scripts"]
    return all((cwd / f).exists() for f in fingerprint)
```

**Usage in the CLI entry point:**

```python
vault_root = find_vault_root()
if vault_root is None:
    if detect_skill_directory():
        print("Error: Running from the skill directory, not a project.")
        print("  Do not cd into the skill directory before invoking the script.")
        print("  Call the script with its full path from your project root.")
        sys.exit(1)
    else:
        print("Error: No .my-tool/ directory found in cwd or any parent.")
        print("  Run 'my-tool config init' to create one here.")
        sys.exit(1)
```

**Why this matters:** Without this check, the user sees a generic "no config found" error. The wrong-directory error is specific and actionable — it tells the agent exactly what it did wrong.

---

## Pattern 4: Bootstrap Escape Hatch

**Problem:** The vault requirement creates a chicken-and-egg problem — `config init` needs to *create* the vault, so it can't require one to exist.

**Solution:** Skip the vault check for bootstrap commands:

```python
# Check for vault (except for 'config init' which creates one)
is_bootstrap = (
    args.command == "config"
    and getattr(args, "config_command", None) == "init"
)
if not is_bootstrap:
    vault_root = find_vault_root()
    if vault_root is None:
        # ... error handling (Pattern 3)
        return 1
```

**Key principle:** Identify the minimal set of commands that must work without config, and gate everything else behind the vault check.

---

## Anti-Patterns

### `git rev-parse --show-toplevel`

```python
# BAD: Breaks when invoked from a different git repository
# (e.g., agent clones a repo into /tmp and runs from there)
import subprocess
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
```

The upward-walk pattern (Pattern 2) is git-agnostic and works in any directory structure.

### Hardcoded paths

```python
# BAD: Assumes a fixed install location
config_path = Path.home() / ".claude" / "skills" / "my-skill" / "config.json"
```

Skills can be installed anywhere — plugin cache, project-local, symlinked dev directories.

### `${CLAUDE_PLUGIN_ROOT}` or similar environment variables

```python
# BAD: Environment variable may not be set in all invocation contexts
root = os.environ["CLAUDE_PLUGIN_ROOT"]
```

Environment variables are unreliable across different agent runtimes and invocation methods.

### Silently defaulting to cwd

```python
# BAD: Silently operates on the wrong directory
config_dir = find_vault_root() or Path.cwd()
# ... proceeds without telling the user there's no vault
```

If no vault is found, **fail loudly** with an actionable error (Pattern 3). Only default to cwd for explicit bootstrap commands (Pattern 4).

---

## How the Patterns Compose

```
Agent receives task
    ↓
SKILL.md tells agent: "CLI is at scripts/my-tool relative to this file"
    ↓                                              [Pattern 1a]
Agent resolves absolute path and invokes CLI
    ↓
CLI resolves its own location via __file__
    ↓                                              [Pattern 1b]
CLI checks: is this a bootstrap command?
    ├── YES → skip vault check                     [Pattern 4]
    └── NO → find_vault_root() walks upward        [Pattern 2]
              ├── FOUND → proceed with config
              └── NOT FOUND → detect_skill_directory()
                              ├── YES → "wrong directory" error  [Pattern 3]
                              └── NO → "no vault found" error
```

---

## References

- Layton skill implementation: `skills/layton/scripts/laytonlib/config.py` — `find_vault_root()`, `detect_skill_directory()`
- Layton CLI entry point: `skills/layton/scripts/laytonlib/cli.py` — vault check with bootstrap escape
- Agent Skills recipe: [agent-skills.md](agent-skills.md) — "Script Path Resolution" section
- Agentic CLI recipe: [agentic-cli.md](agentic-cli.md) — CLI design patterns (complementary; covers flags/output, not discovery)
