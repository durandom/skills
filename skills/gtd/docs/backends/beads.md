# Beads Backend for GTD

The Beads backend uses the [Beads](https://github.com/kortina/beads) issue tracker (bd CLI) for GTD task storage.

## Features

- **Offline-first**: Works offline with Git-based synchronization
- **Persistent context**: Survives conversation compaction in Claude Code
- **Unified database**: Share Beads database with other workflows (email-gather, project management)
- **Git-backed**: All tasks versioned in Git via Dolt

## Setup

### 1. Install Beads

```bash
# Beads requires Dolt database
brew install dolt

# Install beads (via Claude Code plugin or standalone)
# See: https://github.com/kortina/beads
```

### 2. Initialize Beads

```bash
cd your-project
bd init --prefix GTD
```

### 3. Configure GTD to use Beads

```bash
gtd init beads
```

This creates `.gtd/config.json`:

```json
{
  "backend": "beads"
}
```

## Label Mapping

GTD labels are stored as Beads labels with `gtd:` prefix:

| GTD Label | Beads Label |
|-----------|-------------|
| `context/focus` | `gtd:context:focus` |
| `status/active` | `gtd:status:active` |
| `energy/high` | `gtd:energy:high` |
| `horizon/action` | `gtd:horizon:action` |

## Metadata Storage

GTD metadata (due dates, defer, waiting) is stored in the Beads description using YAML frontmatter:

```yaml
---
due: 2026-03-01
defer_until: 2026-02-28
waiting_for:
  person: "Alice"
  reason: "Waiting for design mockups"
blocked_by: [42, 43]
---

Task description goes here...
```

## Integration with Email Briefing

The Layton `email-gather` errand can automatically create GTD tasks from emails:

```bash
# email-gather detects "Action needed" emails
# → Creates GTD task via: gtd add "Pay Vodafone bill" --context focus --due 2026-03-01
# → Stored in Beads database
# → Shows up in: gtd list --status active
```

## Implementation Status

✅ **Implemented**: The Beads backend is fully functional.

**Implemented:**

- ✅ `create_item()` — creates tasks via `bd create`
- ✅ `list_items()` — queries tasks via `bd list --json`
- ✅ `get_item()` — fetches single task via `bd show --json`
- ✅ `update_item()` — updates title, body, labels, project via `bd update`
- ✅ `add_labels()` / `remove_labels()` — incremental label changes
- ✅ `close_item()` / `reopen_item()` — via `bd close` / `bd reopen`
- ✅ `add_comment()` — via `bd comments add`
- ✅ `get_comments()` — Beads-specific bonus method
- ✅ `is_setup()` / `setup()` — bd availability checks
- ✅ Label mapping (`context/focus` ↔ `gtd:context:focus`)
- ✅ Project mapping (`project:<name>` labels)
- ✅ 44 unit tests (mocked subprocess — no bd required in CI)

**Not yet implemented:**

- [ ] Native `--due` / `--defer` bd fields for GTD metadata
- [ ] `waiting_for` via `bd --metadata` JSON field
- [ ] Update SKILL.md with Beads backend docs

## Contributing

See `scripts/gtdlib/backends/beads.py` for the implementation.

Pull requests welcome!

## Example Workflow

```bash
# Initialize
bd init --prefix GTD
gtd init beads

# Capture tasks (goes to Beads)
gtd capture "Review PR for beads backend"

# Clarify into GTD system
gtd inbox
gtd clarify GTD-1

# List tasks (from Beads)
gtd list --context focus --status active

# Mark done (updates Beads)
gtd done GTD-1

# View in Beads directly
bd list --labels gtd
bd show GTD-1
```
