---
name: para
description: PARA method for organizing notes by actionability (Projects, Areas, Resources, Archive). Use for categorization decisions, folder management, and syncing PARA projects with GTD milestones.
---

<essential_principles>

## PARA: Organize by Actionability, Not Topic

PARA organizes information by **when you'll need it**:

| Category | Definition | Key Signal |
|----------|------------|------------|
| **Projects** | Active work with deadlines | "Complete", "deliver", "launch" |
| **Areas** | Ongoing responsibilities, no end date | "Maintain", "manage", "track" |
| **Resources** | Reference material for future use | "Interesting", "might need" |
| **Archive** | Inactive items from above categories | "Done", "paused", "no longer relevant" |

**Example:** A Kubernetes article goes in Projects if deploying now, Areas if maintaining systems, Resources if just learning.

## Folder Structure

```
1_Projects/           # Active work with deadlines
├── _INDEX.md         # Project overview
└── [Project-Name]/   # One folder per project (synced with GTD)

2_Areas/              # Ongoing responsibilities
├── _INDEX.md         # Area overview
└── [area-name].md    # One file per area (or folder if complex)

3_Resources/          # Reference material
├── _INDEX.md         # Resource overview
└── [topic]/          # Topic-based resources

4_Archive/            # Inactive items
├── _INDEX.md         # Archive overview
└── [archived items]  # Completed/inactive content
```

## GTD Sync

PARA projects (`1_Projects/` folders) stay in sync with GTD projects (GitHub milestones):

- **Same names**: `1_Projects/API-Redesign/` ↔ GTD milestone "API-Redesign"
- **Sync command**: `para sync` shows mismatches and offers to fix them
- **One source of truth**: GTD manages project lifecycle, PARA holds the notes

</essential_principles>

<initialization_check>

**IMPORTANT: Before showing the intake menu, run this check:**

```bash
./.claude/skills/para/scripts/para status 2>/dev/null
```

If it exits non-zero or shows "Error: PARA root not configured", the user needs to initialize PARA first.

**Do NOT proceed to intake.** Instead:

1. Use `AskUserQuestion` to ask: "Where would you like to store your PARA files?"
   - Offer sensible options like `~/Notes`, `~/Documents/PARA`, or let them specify a custom path
   - Ask if this should be the default for all projects or just this repo
2. After getting the path, run:

   ```bash
   # Initialize PARA structure
   ./.claude/skills/para/scripts/para init --path <user-specified-path>

   # Then save config (choose one):
   # For this repo only:
   ./.claude/skills/para/scripts/para config --set-repo . <user-specified-path>
   # Or as global default:
   ./.claude/skills/para/scripts/para config --set-root <user-specified-path>
   ```

3. Then proceed to the intake menu.

</initialization_check>

<intake>
What would you like to do?

1. **Categorize** - Help deciding where something belongs
2. **Sync** - Check/sync PARA projects with GTD milestones
3. **Review** - Audit PARA structure for stale items
4. **Create** - Set up new project/area/resource folder
5. **Archive** - Move completed items to archive

**Wait for response before proceeding.**
</intake>

<routing>

| Response | Workflow |
|----------|----------|
| 1, "categorize", "where", "which category", "decide" | `workflows/categorize.md` |
| 2, "sync", "gtd", "milestones", "projects" | `workflows/sync-projects.md` |
| 3, "review", "audit", "stale", "cleanup" | `workflows/review.md` |
| 4, "create", "new", "add", "setup" | `workflows/create.md` |
| 5, "archive", "done", "complete", "move" | `workflows/archive.md` |
| Other | Clarify intent, then select appropriate workflow |

**After reading the workflow, follow it exactly.**
</routing>

<quick_reference>

## CLI Commands

```bash
PARA="./.claude/skills/para/scripts/para"

# Show PARA structure status
$PARA status

# Show/manage configuration
$PARA config

# Configuration options:
$PARA config --set-root ~/Notes           # Set global default
$PARA config --set-repo . ~/Notes/work    # Map current repo → PARA location
$PARA config --unset-repo .               # Remove repo mapping

# Sync with GTD (shows mismatches)
$PARA sync

# Sync and fix mismatches
$PARA sync --fix

# Create new project (also creates GTD milestone)
$PARA project create "Project-Name"

# Archive a project
$PARA project archive "Project-Name"

# List projects (with GTD sync status)
$PARA project list
```

## Configuration Resolution

PARA root is resolved in order:

1. `.para.toml` in current git repo root (local override)
2. `[repos]` mapping in `~/.config/para/config.toml` (per-repo)
3. `para_root` in global config (default)
4. Auto-discovery (walk up from cwd looking for PARA folders)

## Decision Tree

```
Is this actively being worked on with a deadline?
├── YES → 1_Projects/
└── NO ↓

Is this an ongoing responsibility I maintain?
├── YES → 2_Areas/
└── NO ↓

Is this something I might reference later?
├── YES → 3_Resources/
└── NO ↓

Is this completed/inactive but worth keeping?
├── YES → 4_Archive/
└── NO → Delete it
```

</quick_reference>

<reference_index>

## Domain Knowledge

All in `references/`:

- **para-method.md** - Full PARA methodology with examples

</reference_index>

<workflows_index>

## Workflows

All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| categorize.md | Help decide where items belong |
| sync-projects.md | Sync PARA projects with GTD milestones |
| review.md | Audit PARA structure for stale/misplaced items |
| create.md | Create new PARA folders with proper structure |
| archive.md | Move items to archive with proper handling |

</workflows_index>
