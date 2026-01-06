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
1 Projects/           # Active work with deadlines
├── _INDEX.md         # Project overview
└── [Project-Name]/   # One folder per project (synced with GTD)

2 Areas/              # Ongoing responsibilities
├── _INDEX.md         # Area overview
└── [area-name].md    # One file per area (or folder if complex)

3 Resources/          # Reference material
├── _INDEX.md         # Resource overview
└── [topic]/          # Topic-based resources

4 Archive/            # Inactive items
├── _INDEX.md         # Archive overview
└── [archived items]  # Completed/inactive content
```

## GTD Sync

PARA projects (`1 Projects/` folders) stay in sync with GTD projects (GitHub milestones):

- **Same names**: `1 Projects/API-Redesign/` ↔ GTD milestone "API-Redesign"
- **Sync command**: `para sync` shows mismatches and offers to fix them
- **One source of truth**: GTD manages project lifecycle, PARA holds the notes

</essential_principles>

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

## Decision Tree

```
Is this actively being worked on with a deadline?
├── YES → 1 Projects/
└── NO ↓

Is this an ongoing responsibility I maintain?
├── YES → 2 Areas/
└── NO ↓

Is this something I might reference later?
├── YES → 3 Resources/
└── NO ↓

Is this completed/inactive but worth keeping?
├── YES → 4 Archive/
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
