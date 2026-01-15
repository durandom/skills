# Research: Layton (Personal AI Assistant)

**Branch**: `001-pai-orchestrator` | **Date**: 2026-01-13

## Research Questions

| ID | Question | Status |
|----|----------|--------|
| R1 | Concurrent vs sequential skill queries for <60s target | ✅ Resolved |
| R2 | Personal configuration storage location | ✅ Resolved (updated) |
| R3 | Skill CLI invocation patterns | ✅ Resolved |
| R4 | State management approach | ✅ Resolved |
| R5 | Skill interaction architecture | ✅ Resolved |

---

## R1: Sequential vs Concurrent Skill Queries

### Decision

#### Use sequential skill queries (start simple)

### Rationale

1. **Simplicity first**: Sequential is the simplest approach with no threading complexity
2. **Defer optimization**: Can add concurrency later if 60s target is at risk in practice
3. **Easier debugging**: Linear execution is easier to trace and debug
4. **Skills are fast**: Most skill CLIs complete in <5s, so sequential may still meet target

### Implementation

```python
def query_skills(skills: list[str]) -> dict:
    """Query skills sequentially."""
    results = {}
    for skill in skills:
        try:
            results[skill] = invoke_skill(skill, "list", "--json")
        except Exception as e:
            logger.warning(f"{skill} failed: {e}")
            # Continue with available results
    return results
```

### Latency Budget (Sequential)

| Component | Typical | Worst | Budget |
|-----------|---------|-------|--------|
| Sequential skill queries (3 skills) | 15s | 30s | 45s |
| AI synthesis | 10-20s | 30s | 15s |
| **Total** | 25-50s | 60s | **60s** |

### Future Optimization

If sequential exceeds 60s target in practice, can upgrade to:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(invoke_skill, s, "list", "--json"): s for s in skills}
    for future in as_completed(futures, timeout=45):
        results[futures[future]] = future.result()
```

### Alternatives Considered

| Alternative | Status |
|-------------|--------|
| ThreadPoolExecutor | Deferred - adds complexity, use if sequential too slow |
| asyncio | Rejected - overkill for subprocess I/O |
| Caching | Rejected - spec forbids (FR-008 single source of truth) |

---

## R2: Personal Configuration Storage

### Decision

**Repo-local `.layton/config.json` for configuration only**

```
.layton/
└── config.json    # Personal configuration only (state handled by Beads)
```

### Rationale

1. **Skill executes in target repo**: Layton runs where the user's work lives
2. **Portable**: Project can be moved/shared with settings intact
3. **Gitignore-able**: Add `.layton/` to `.gitignore` to keep personal data private
4. **State via Beads**: No custom state files needed (see R4)

### Schema Structure

```json
{
  "$schema": "layton-config-v1",
  "work_schedule": {
    "start": "HH:MM",
    "end": "HH:MM"
  },
  "timezone": "IANA timezone string",
  "personality": {
    "verbosity": "terse | normal | verbose",
    "tone": "professional | casual | friendly",
    "humor": boolean,
    "explanation_level": "concise | detailed | teaching"
  },
  "interaction": {
    "proactive_clarification": boolean,
    "teaching_mode": boolean,
    "semantic_zoom_default": "summary | detail"
  }
}
```

### Config Resolution

```python
def find_config() -> Path | None:
    git_root = get_git_root()
    if git_root and (config := git_root / ".layton" / "config.json").exists():
        return config
    return None  # Use defaults
```

### Alternatives Rejected

| Alternative | Why Rejected |
|-------------|--------------|
| `~/.config/layton/` | Skill runs in target repo, not home; loses project context |
| `.layton/state.json` | State handled by Beads (see R4) |
| Two-tier (home + repo) | Unnecessary complexity for single-user skill |

---

## R3: Skill CLI Invocation Patterns

### Findings

**Existing skills follow consistent patterns:**

#### Standard Subcommands

| Command | Purpose | Skills Using |
|---------|---------|--------------|
| `list` | Query with filters | GTD, PARA |
| `show` | Single item details | GTD, meeting-notes |
| `daily/weekly` | Review workflows | GTD |
| `sync` | External synchronization | meeting-notes |

#### Output Format Contract

```python
# Always support --json for machine parsing
result = subprocess.run(
    [skill_cli, "list", "--json"],
    capture_output=True,
    text=True
)

# JSON structure
{
    "success": true,
    "data": [...],
    "next_steps": [{"command": "...", "description": "..."}]
}
```

#### Exit Code Contract

| Code | Meaning |
|------|---------|
| 0 | Success (including dry-run/preview) |
| 1 | Error (operation failed) |
| 2 | User input error (validation) |

#### Subprocess Invocation Pattern

```python
def invoke_skill(skill: str, *args) -> dict:
    """Invoke a skill CLI with JSON output."""
    cli_path = find_skill_cli(skill)
    result = subprocess.run(
        [cli_path, *args, "--json"],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"success": False, "error": result.stderr or result.stdout}

    return json.loads(result.stdout)
```

### Key Patterns for Layton

1. **Always use --json** for deterministic parsing
2. **Check returncode first**, then parse stdout
3. **Set timeouts** (30s default, 45s for expensive ops)
4. **Capture both stdout and stderr** for debugging
5. **Include next_steps** in output for agentic CLI pattern

---

## R4: State Management - Beads Integration

### Decision

**Use [Beads](https://github.com/steveyegge/beads) for all state management**

### What is Beads?

Beads is a "distributed, git-backed graph issue tracker for AI agents." Key features:

- **Git as primary store**: Tasks as JSONL in `.beads/`, version controlled
- **SQLite for performance**: Local cache layer
- **Hash-based IDs**: `bd-a1b2` format eliminates merge conflicts
- **Dependency tracking**: Auto-ready detection when blockers resolve
- **Semantic memory decay**: Compacts old closed tasks

### Why Beads for Layton?

| Benefit | Impact |
|---------|--------|
| No custom state files | Eliminates `.layton/state.json` |
| No schema migrations | Beads handles evolution |
| Git-backed history | Full audit trail |
| AI-native design | Optimized for agent workflows |
| Distributed support | Multi-agent scenarios if needed |

### What Layton Stores in Beads

| State Type | Bead Representation |
|------------|---------------------|
| Current focus | Bead with "focus" tag |
| In-progress task | Link to task bead |
| Interaction history | Audit trail in bead history |
| Planning horizon | Beads with deadline metadata |

### What Layton Does NOT Store

- **Skill data**: Queried live via CLI (FR-008 single source of truth)
- **Unified views**: Generated at runtime by SKILL.md workflows
- **Attention items**: Computed by SKILL.md from skill data

### Beads CLI Integration

```python
def get_current_focus() -> str | None:
    """Get current focus from Beads."""
    result = subprocess.run(
        ["bd", "list", "--tag", "focus", "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data.get("current_focus")
    return None
```

### Alternatives Rejected

| Alternative | Why Rejected |
|-------------|--------------|
| Custom `.layton/state.json` | Reinvents wheel; Beads is purpose-built |
| SQLite directly | Loses git-backing and AI-native features |
| In-memory only | No persistence across sessions |

---

## R5: Skill Interaction Architecture

### Decision

#### Two-layer model: SKILL.md (probabilistic) + CLI (deterministic)

### The Model

```
┌─────────────────────────────────────────────────────────────────┐
│       SKILL.md (Probabilistic - AI Judgment)                    │
│  • Interprets user intent                                       │
│  • Synthesizes information from multiple skills                 │
│  • Applies persona voice (Elizabeth Layton)                     │
│  • Routes requests to workflows                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ invokes for data
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               CLI (Deterministic - Data Operations)             │
│  • layton gather: Discover and query skills                     │
│  • layton context: Temporal context                             │
│  • layton note: Route capture to skill                          │
│  • layton config: Personal preferences                          │
│  • layton doctor: Health check                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Split?

| Operation | Deterministic? | Handler |
|-----------|----------------|---------|
| Querying skill CLIs | Yes | CLI |
| Getting current time | Yes | CLI |
| Routing a note capture | Yes | CLI |
| Synthesizing a briefing | No | SKILL.md |
| Deciding urgency | No | SKILL.md |
| Entity correlation | No | SKILL.md |

### Skill Discovery (Skill-Agnostic)

The CLI doesn't know about specific skills. It discovers them at runtime:

```python
def discover_skills() -> list[dict]:
    """Find available skills at runtime."""
    skills = []
    for skill_dir in [Path("./skills"), Path("./.claude/skills")]:
        if skill_dir.exists():
            for path in skill_dir.iterdir():
                if (path / "SKILL.md").exists() and (path / "scripts").exists():
                    skills.append({
                        "name": path.name,
                        "path": str(path),
                        "has_capture": has_capture_command(path)
                    })
    return skills
```

### Skill-to-Skill Communication

From FR-002: "reads target SKILL.md for context, invokes CLIs for operations"

```
User: "What's happening with Project X?"
           │
           ▼
┌─────────────────────────────────────┐
│      Layton SKILL.md Workflow       │
│  1. Run `layton gather --json`      │
│  2. For each skill with data:       │
│     - Read skill's SKILL.md         │
│     - Invoke skill CLI if needed    │
│  3. Synthesize with Layton voice    │
└─────────────────────────────────────┘
```

### Alternatives Rejected

| Alternative | Why Rejected |
|-------------|--------------|
| CLI does synthesis | Mixes AI work into deterministic code |
| Hardcoded skill names | Not skill-agnostic; breaks if skill missing |
| Import skill modules | Creates code dependencies; violates loose coupling |

---

## Implementation Checklist

- [x] R1: Concurrent query architecture decided
- [x] R2: Personal config storage location decided
- [x] R3: CLI invocation patterns documented
- [x] R4: State management via Beads decided
- [x] R5: Skill interaction architecture documented
- [ ] Implement skill discovery
- [ ] Implement Beads integration helpers
- [ ] Define config schema validation
