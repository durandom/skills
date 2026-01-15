# CLI Contract: layton

**Version**: 3.0.0 | **Date**: 2026-01-13

## Overview

The `layton` CLI handles **deterministic operations only**. All probabilistic work (AI judgment, synthesis, persona) lives in SKILL.md workflows executed by Claude.

**Design Philosophy:**

- CLI is skill-agnostic: discovers available skills at runtime
- No AI synthesis in CLI: just data operations
- State managed by Beads: CLI only handles personal configuration
- Output includes "Next steps" for agentic CLI pattern

---

## Command Structure

```
layton [command] [options]

Commands:
  gather       Discover and query available skills
  context      Get current temporal context
  note         Route capture to appropriate skill
  config       Manage personal configuration (JSON settings)
  preferences  Manage behavioral instructions (prose)
  doctor       Validate setup and skill availability

Options:
  --json     Machine-readable output (required for SKILL.md workflows)
  --verbose  Debug information
  --help     Show help
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--json` | Output in machine-readable JSON format |
| `--verbose` | Include debug information |
| `--help` | Show command help |

---

## Commands

### `layton gather`

Discover available skills and query them for data. This is the primary data-gathering command used by SKILL.md workflows.

```bash
layton gather [--skills name1,name2] [--json]
```

**Options:**

- `--skills`: Comma-separated list of skills to query (default: all available)

**Exit Codes:**

- 0: Success (even if some skills unavailable)
- 1: No skills available

**JSON Output:**

```json
{
  "success": true,
  "timestamp": "2026-01-13T08:00:00Z",
  "skills_available": ["gtd", "para", "meeting-notes"],
  "skills_queried": ["gtd", "para"],
  "skills_unavailable": ["calendar"],
  "data": {
    "gtd": {
      "inbox_count": 5,
      "active_tasks": [
        {"id": "123", "title": "Review API design", "context": "focus"}
      ]
    },
    "para": {
      "projects": ["Project-X", "Project-Y"],
      "areas": ["Engineering", "Health"]
    }
  },
  "next_steps": [
    {"command": "layton context", "description": "Get temporal context for synthesis"}
  ]
}
```

**Skill Discovery:**

The CLI searches for skills in these locations:

1. `./skills/` - User/project-level skills
2. `./.claude/skills/` - Framework-level skills

A valid skill has both `SKILL.md` and `scripts/` directory.

---

### `layton context`

Returns current temporal context for SKILL.md workflow decision-making. No skill-specific state—just time and work hours.

```bash
layton context [--json]
```

**JSON Output:**

```json
{
  "success": true,
  "timestamp": "2026-01-13T08:30:00Z",
  "time_of_day": "morning",
  "day_of_week": "monday",
  "work_hours": true,
  "timezone": "America/Los_Angeles",
  "next_steps": [
    {"command": "layton gather", "description": "Gather data from available skills"}
  ]
}
```

**Time of Day Classification:**

| Range | Classification |
|-------|----------------|
| 05:00-11:59 | morning |
| 12:00-13:59 | midday |
| 14:00-17:59 | afternoon |
| 18:00-21:59 | evening |
| 22:00-04:59 | night |

**Work Hours:**

Determined from `.layton/config.json` (defaults to 09:00-17:00 if not configured).

---

### `layton note "<text>"`

Quick capture routed to appropriate skill. The CLI discovers available capture-capable skills and routes to the first one found.

```bash
layton note "<text>" [--json]
```

**Arguments:**

- `text`: The raw thought, task, or note to capture

**Exit Codes:**

- 0: Successfully captured
- 1: No capture-capable skill available (stores locally)

**JSON Output:**

```json
{
  "success": true,
  "text": "call dentist tomorrow",
  "routed_to": "gtd",
  "destination": "inbox",
  "item_id": "task-456",
  "next_steps": [
    {"command": "gtd clarify", "description": "Process inbox items"}
  ]
}
```

**Routing Priority:**

1. Skills with `capture` command (e.g., GTD)
2. Local storage (`.layton/notes.jsonl`) if no skill available

**Note:** The CLI doesn't know about GTD specifically—it discovers skills at runtime that support capture operations.

---

### `layton config <subcommand>`

Manage personal configuration. This is the only persistent data Layton maintains (state is handled by Beads).

```bash
layton config show [--json]
layton config set <key> <value>
layton config init
```

**Subcommands:**

- `show`: Display current configuration
- `set`: Update a config value (dot notation supported)
- `init`: Create default config file

**Config File:** `.layton/config.json`

**JSON Output (show):**

```json
{
  "success": true,
  "source": ".layton/config.json",
  "config": {
    "work_schedule": {
      "start": "09:00",
      "end": "17:00"
    },
    "timezone": "America/Los_Angeles",
    "personality": {
      "verbosity": "terse",
      "tone": "professional",
      "humor": false
    },
    "interaction": {
      "proactive_clarification": true,
      "teaching_mode": false,
      "semantic_zoom_default": "summary"
    }
  },
  "next_steps": []
}
```

**Config Schema:**

```json
{
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

---

### `layton preferences <subcommand>`

Manage behavioral instructions stored in `.layton/preferences.md`. Unlike config (structured JSON), preferences are prose that guide AI behavior.

```bash
layton preferences show [--json]
layton preferences add "<instruction>" [--section "Section Name"]
layton preferences init
```

**Subcommands:**

- `show`: Display current preferences (returns markdown content)
- `add`: Append an instruction to a section (creates section if needed)
- `init`: Create default preferences file with example structure

**Preferences File:** `.layton/preferences.md`

**JSON Output (show):**

```json
{
  "success": true,
  "source": ".layton/preferences.md",
  "exists": true,
  "sections": ["Email Handling", "Morning Routine", "People I Track"],
  "content": "# My Layton Preferences\n\n## Email Handling\n- Only surface starred messages\n...",
  "next_steps": []
}
```

**JSON Output (add):**

```json
{
  "success": true,
  "action": "added",
  "section": "People I Track",
  "instruction": "Platform team - monitor for API-related updates",
  "next_steps": []
}
```

**Example Usage:**

```bash
# View current preferences
layton preferences show

# Add to existing section
layton preferences add "Platform team - monitor for API updates" --section "People I Track"

# Add to new section (creates it)
layton preferences add "Focus on release-blocking tickets" --section "Jira Priorities"

# Initialize with defaults
layton preferences init
```

**Note:** The `add` command is deterministic (append text to file). The SKILL.md workflow handles conversational preference discovery and calls this command after user confirmation.

---

### `layton doctor`

Validate setup and skill availability. Follows the agentic CLI pattern with hidden `--fix` flag.

```bash
layton doctor [--fix] [--json]
```

**Options:**

- `--fix`: Auto-fix issues (HIDDEN from --help, shown in next_steps)

**Exit Codes:**

- 0: All checks pass
- 1: Issues found (fixable with --fix)
- 2: Critical issues (manual intervention required)

**JSON Output:**

```json
{
  "success": true,
  "checks": [
    {"name": "config_exists", "status": "pass", "message": "Config file found"},
    {"name": "config_valid", "status": "pass", "message": "Config schema valid"},
    {"name": "preferences_exists", "status": "pass", "message": "Preferences file found"},
    {"name": "preferences_valid", "status": "pass", "message": "Preferences file is valid markdown"},
    {"name": "beads_available", "status": "pass", "message": "Beads CLI found"},
    {"name": "skills_detected", "status": "pass", "message": "3 skills available", "count": 3}
  ],
  "skills_available": ["gtd", "para", "meeting-notes"],
  "fixable": [],
  "next_steps": []
}
```

**Checks Performed:**

| Check | Description |
|-------|-------------|
| `config_exists` | `.layton/config.json` exists |
| `config_valid` | Config file parses and matches schema |
| `preferences_exists` | `.layton/preferences.md` exists (warn if missing, not error) |
| `preferences_valid` | Preferences file is valid markdown (parseable) |
| `beads_available` | Beads CLI is available for state management |
| `skills_detected` | At least one skill is available |

---

## Error Format

All errors follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "SKILL_UNAVAILABLE",
    "message": "No capture-capable skill found",
    "details": "Searched: ./skills/, ./.claude/skills/"
  },
  "next_steps": [
    {"command": "layton doctor", "description": "Check skill availability"}
  ]
}
```

**Error Codes:**

| Code | Description |
|------|-------------|
| `CONFIG_MISSING` | No config file found |
| `CONFIG_INVALID` | Config file has schema errors |
| `SKILL_UNAVAILABLE` | Requested skill not found |
| `SKILL_TIMEOUT` | Skill query timed out |
| `SKILL_ERROR` | Skill returned non-zero exit code |
| `BEADS_UNAVAILABLE` | Beads CLI not found |
| `NO_CAPTURE_SKILL` | No skill supports capture operation |

---

## Progressive Disclosure

The `--fix` flag for `doctor` is intentionally hidden from `--help` output. It appears in:

1. JSON output `next_steps` when issues are fixable
2. Text output "Next steps" section

This follows the agentic CLI pattern: safe operations are visible, potentially destructive operations are discovered through context.

---

## What's NOT in the CLI

These operations are handled by SKILL.md workflows (probabilistic):

| Operation | Why Not CLI |
|-----------|-------------|
| Morning briefing | Requires AI synthesis |
| Focus suggestion | Requires AI judgment about priorities |
| Cross-system query | Requires semantic entity correlation |
| Periodic reviews | Requires AI interpretation of progress |
| Attention item surfacing | Requires AI urgency assessment |

The CLI provides **data** that SKILL.md workflows consume for **synthesis**.
