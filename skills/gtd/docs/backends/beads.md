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

⚠️ **Work in Progress**: The Beads backend is currently a stub implementation.

**Completed:**
- ✅ Backend structure and configuration
- ✅ Label mapping logic
- ✅ Integration with GTD config system

**TODO:**
- [ ] Implement `add_item()` - Create tasks in Beads
- [ ] Implement `list_items()` - Query tasks from Beads
- [ ] Implement `get_item()` - Fetch single task
- [ ] Implement `update_item()` - Modify task labels/metadata
- [ ] Implement `close_item()` - Mark task complete
- [ ] Implement `add_comment()` - Add comments to tasks
- [ ] Implement `get_comments()` - Retrieve task comments
- [ ] Add tests for Beads backend
- [ ] Update SKILL.md with Beads backend docs

## Contributing

See `scripts/gtdlib/backends/beads.py` for the implementation. All methods are currently stubbed with `NotImplementedError` and marked with `TODO` comments.

Pull requests welcome!

## Example Workflow

Once fully implemented, the workflow will be:

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
