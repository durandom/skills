---
name: gtd
description: GTD task management with Python CLI. Use for capturing, clarifying, organizing, and reviewing tasks following David Allen's Getting Things Done methodology with proper Horizons of Focus support.
---

<essential_principles>

## GTD Core Workflow

1. **Capture** - Get it out of your head into the system
2. **Clarify** - Is it actionable? What's the next action?
3. **Organize** - Add context, energy, status, horizon labels
4. **Reflect** - Daily/weekly/quarterly/yearly reviews keep system trusted
5. **Engage** - Work from filtered lists, not full backlog

## Running the CLI

All GTD operations go through the `gtd` CLI. Execute from the **repo root** (not the skill directory):

```bash
# Run from repo root - script auto-detects repo context
./.claude/skills/gtd/scripts/gtd <command>
```

**Setup is automatic**: The CLI will detect if labels are missing and create them on first use.

## Label Taxonomy (12 Fixed Labels)

Never create new labels. See [label-taxonomy.md](references/label-taxonomy.md).

- **Context**: focus, meetings, async, offsite (where/when)
- **Energy**: high, low (cognitive load)
- **Status**: active, waiting, someday (workflow state)
- **Horizon**: action, project, goal (GTD altitude)

## GTD Horizons of Focus

The system supports David Allen's 6 Horizons:

| Horizon | Name | Implementation |
|---------|------|----------------|
| Ground | Actions | `horizon/action` label via gtd CLI |
| H1 | Projects | `horizon/project` label + project grouping |
| H2 | Areas of Focus | Ongoing responsibilities without end dates |
| H3 | Goals | `horizon/goal` label via gtd CLI |
| H4 | Vision | `HORIZONS.md` at vault root |
| H5 | Purpose | `HORIZONS.md` at vault root |

**Setup:** Copy the template to your vault root:

```bash
cp .claude/skills/gtd/references/horizons.md HORIZONS.md
```

</essential_principles>

<intake>
What would you like to do?

1. Capture something new
2. Process inbox (clarify items)
3. Find tasks to work on
4. Do a review (daily/weekly/quarterly/yearly)
5. Manage projects

**Wait for response before proceeding.**
</intake>

<routing>

| Response | Command |
|----------|---------|
| 1, "capture", "add something" | `./gtd capture "<text>"` |
| 2, "inbox", "process", "clarify" | `./gtd inbox` then `./gtd clarify <id>` |
| 3, "list", "find", "work", "tasks" | `./gtd list --status active --context <context>` |
| 4a, "daily review" | `./gtd daily` |
| 4b, "weekly review" | `./gtd weekly` |
| 4c, "quarterly review" | `./gtd quarterly` |
| 4d, "yearly review" | `./gtd yearly` |
| 4e, "review status", "when did I" | `./gtd reviews` |
| 5, "projects" | `./gtd projects` or `./gtd project list` |
| 5a, "create project" | `./gtd project create "<title>"` |
| 5b, "show project", "project details" | `./gtd project show "<title>"` |
| 5c, "delete project" | `./gtd project delete "<title>"` |

**After determining intent, execute commands from repo root using `./.claude/skills/gtd/scripts/gtd`.**
</routing>

<quick_start>

```bash
# Run from repo root - script auto-detects repo context
GTD="./.claude/skills/gtd/scripts/gtd"

# Capture something (goes to inbox)
$GTD capture "Review PR for plugin architecture"

# See what needs clarifying
$GTD inbox

# Clarify an item (interactive)
$GTD clarify 42

# Add a pre-clarified action
$GTD add "Write RFE draft" --context focus --energy high --status active

# Add a project
$GTD add "Promotion to Senior Principal" --horizon project

# Add an action to a project
$GTD add "Schedule skip-level with director" --horizon action --project "Promotion to Senior Principal"

# Add a yearly goal
$GTD add "2026: Improve fitness" --horizon goal

# Find morning focus work
$GTD list --context focus --energy high --status active

# View projects with progress
$GTD projects

# Project management
$GTD project list                              # List all projects
$GTD project show "Promotion to Senior Principal"
$GTD project create "Launch sidekick MVP" --desc "Ship v1.0" --due 2026-06-30
$GTD project update "Launch sidekick MVP" --state closed  # Mark complete
$GTD project delete "Abandoned idea" --force   # Delete project

# Daily review
$GTD daily

# Weekly review
$GTD weekly

# Quarterly review
$GTD quarterly

# Yearly review
$GTD yearly

# Check review status
$GTD reviews

# View action history
$GTD history
$GTD history --limit 50
$GTD history --since 2026-01-15

# Mark done
$GTD done 42
```

</quick_start>

<command_reference>

| Command | Purpose |
|---------|---------|
| `capture <text>` | Quick capture to inbox |
| `inbox` | List items needing clarification |
| `clarify <id>` | Interactive clarification workflow |
| `add <title>` | Add a clarified task with labels |
| `list [filters]` | List tasks with optional filters |
| `view <id>` | View task details with GTD labels |
| `done <id>` | Mark task complete (single ID only) |
| `update <id> [flags]` | Update task GTD labels |
| `comment <id> <text>` | Add comment to task |
| `due <id> [date]` | Set due date (YYYY-MM-DD), or view if no date |
| `due <id> --clear` | Remove due date |
| `defer <id> <date>` | Defer until date, optionally `--someday` |
| `waiting <id> <person> [reason]` | Mark as waiting on someone |
| `blocked <id> [ids]` | Set blockers (comma-separated), `--clear` to remove |
| `next [--context] [--energy]` | Get suggested next action |
| `bulk <ids> [flags]` | Bulk update (IDs: comma-separated or ranges like `1-5`) |
| `bulk <ids> --close` | Close multiple items at once |
| `projects` | List projects with progress (alias for `project list`) |
| `project list` | List projects with progress |
| `project show <title>` | Show project details and actions |
| `project create <title>` | Create a new project |
| `project update <title>` | Update project (desc, due, state, rename) |
| `project delete <title>` | Delete a project |
| `daily` | Daily review workflow (auto-marks complete) |
| `weekly` | Weekly review workflow (auto-marks complete) |
| `quarterly` | Quarterly review (auto-marks complete) |
| `yearly` | Yearly review (auto-marks complete) |
| `reviews` | Show detailed review status and cadences |
| `history` | Show action history log |
| `setup [--check]` | Check/create labels (auto-runs on first use) |

**Common filters for `list`:**

- `--context focus|meetings|async|offsite`
- `--energy high|low`
- `--status active|waiting|someday`
- `--horizon action|project|goal`
- `--project "Project Name"`

**Project command options:**

- `project list [--state open|closed|all]`
- `project create <title> [--desc] [--due YYYY-MM-DD]`
- `project update <title> [--desc] [--due] [--state open|closed] [--rename]`
- `project delete <title> [--force]` (warns if open actions exist)

**Review tracking:**

- `reviews` - Show when each review was last done and if overdue
- `reviews --reset daily` - Reset review timestamp (for testing)
- Reviews auto-mark complete when you run `daily`, `weekly`, `quarterly`, `yearly`
- Cadences: daily=1 day, weekly=7 days, quarterly=90 days, yearly=365 days

**History log:**

- `history` - Show last 20 actions (human-readable)
- `history --limit 50` - Show more entries
- `history --since 2026-01-15` - Filter by date
- `history --json` - Raw JSONL output (machine-readable)
- Logs stored in `.gtd/history.log`
</command_reference>

<workflows>

**Morning routine:**

```bash
$GTD daily
# Shows: High energy focus → Light focus → Async → Waiting
```

**Between meetings:**

```bash
$GTD list --energy low --status active
# Shows quick tasks (5-15 min each)
```

**Weekly planning:**

```bash
$GTD weekly
# Process inbox, review active items, check projects
```

**Quarterly planning:**

```bash
$GTD quarterly
# Review goals, project progress, set next quarter focus
```

**Yearly planning:**

```bash
$GTD yearly
# Review vision, set yearly goals, reflect on purpose
```

</workflows>

<success_criteria>

- All items captured go through clarification
- Inbox is empty after processing
- Every project has at least one active action
- Reviews happen: daily (5 min), weekly (15 min), quarterly (1 hr), yearly (2 hr)
- Work from filtered context lists, not full backlog
- All operations go through the `./gtd` CLI
</success_criteria>

<reference_index>

- [clarify-flowchart.md](references/clarify-flowchart.md) - GTD decision tree with 2-minute rule
- [label-taxonomy.md](references/label-taxonomy.md) - Complete 12-label reference
- [gtd-workflow.md](references/gtd-workflow.md) - GTD methodology details
- [horizons.md](references/horizons.md) - Template for HORIZONS.md (copy to vault root)
- [clarify-decision-tree.md](references/clarify-decision-tree.md) - Decision trees for clarification, context, priority, reviews
- [common-mistakes.md](references/common-mistakes.md) - GTD anti-patterns and fixes
- [complementary-skills.md](references/complementary-skills.md) - How PARA complements GTD (informational)

**Review Workflows (agent-consumable instructions):**

- [daily-review.md](workflows/daily-review.md) - Daily review guide
- [weekly-review.md](workflows/weekly-review.md) - Weekly review guide
- [quarterly-review.md](workflows/quarterly-review.md) - Quarterly review guide
- [yearly-review.md](workflows/yearly-review.md) - Yearly review guide
</reference_index>
