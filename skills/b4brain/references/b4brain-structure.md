# b4brain Structure Reference

<overview>
This reference documents the specific folder structure, naming conventions, and metadata files used in the b4brain implementation of PARA/GTD/Zettelkasten.
</overview>

<folder_structure>

## Complete Folder Structure

```
brainz/                         # Root of Obsidian vault
│
├── inbox/                      # GTD Capture Layer
│   ├── SCRATCH.md             # Primary quick capture file
│   └── [captured-items]/      # Larger captures awaiting processing
│
├── 1 Projects/                 # PARA: Active work with deadlines
│   ├── _INDEX.md              # Project overview and navigation
│   ├── [Project-Name]/        # Folder for multi-file projects
│   │   ├── README.md          # Project definition
│   │   └── [project files]    # Supporting materials
│   └── [project-name.md]      # Single-file projects
│
├── 2 Areas/                    # PARA: Ongoing responsibilities
│   ├── _INDEX.md              # Area overview
│   └── [area-name.md]         # One file per area (or folder if complex)
│
├── 3 Resources/                # PARA: Reference materials
│   ├── _INDEX.md              # Resource overview by topic
│   ├── zettelkasten/          # Knowledge graph (see below)
│   └── [topic]/               # Topic-organized references
│
├── 4 Archive/                  # PARA: Inactive items
│   ├── _INDEX.md              # Archive overview
│   ├── projects/              # Completed/abandoned projects
│   └── [year]/                # Time-based organization
│
├── _GTD_TASKS.md              # Central GTD task list
│
├── docs/                       # System documentation
│   ├── b4brain.md             # System overview
│   └── research.md            # Methodology research
│
├── .claude/                    # Claude configuration
│   ├── commands/              # Slash commands
│   ├── skills/                # Skills library
│   └── metadata/              # System state (JSON)
│
└── CLAUDE.md                   # Project instructions for Claude
```

</folder_structure>

<zettelkasten_structure>

## Zettelkasten Structure

```
3 Resources/zettelkasten/
├── concepts/                   # Atomic permanent notes
│   └── YYYYMMDD-concept-name.md
├── patterns/                   # Recurring patterns and templates
│   └── pattern-name.md
├── connections/                # Maps of content (MOCs)
│   └── topic-connections.md
└── _GRAPH.md                  # Knowledge graph overview
```

**File naming:**

- Concepts: `YYYYMMDD-kebab-case-name.md` (date prefix for chronology)
- Patterns: `kebab-case-name.md`
- Connections: `topic-connections.md`
</zettelkasten_structure>

<index_files>

## Index Files (_INDEX.md)

Each PARA folder contains an `_INDEX.md` for navigation:

**Structure:**

```markdown
# [Category] Index

## Overview
[Brief description of this category's purpose]

## Contents

### [Subcategory 1]
- [[Item 1]] - Brief description
- [[Item 2]] - Brief description

### [Subcategory 2]
- [[Item 3]] - Brief description

## Recently Added
- [Date]: [[New Item]] - What it is

## Notes
[Any category-specific notes or conventions]
```

**Maintenance:**

- Updated by `/index` command
- General categories only (avoid specific tool names)
- Links use Obsidian wiki-link format
</index_files>

<gtd_tasks_format>

## GTD Tasks File (_GTD_TASKS.md)

**Structure:**

```markdown
# GTD Task List

## @computer
- [ ] Task description ⚠️ [Project-Reference]
- [ ] Task description 🔥 Due: Friday [Project-Reference]

## @calls
- [ ] Task description ⚠️ [Area-Reference]

## @office
- [ ] Task description 💡

## @home
- [ ] Personal task description

## @anywhere
- [ ] Task that can be done anywhere

## @waiting
- [ ] Waiting for: Person - what 🔥 [Project-Reference]

## @review
- [ ] Item needing deeper thinking ⚠️

## Someday/Maybe
- [ ] Future possibility
- [ ] Thing to explore someday
```

**Priority indicators:**

- 🔥 High - Urgent/critical
- ⚠️ Medium - Important
- 💡 Low - Nice to have

**Context tags:**

- `@computer` - Requires computer
- `@calls` - Phone/video calls
- `@office` - Must be at office
- `@home` - Must be at home
- `@anywhere` - Can do anywhere
- `@waiting` - Delegated/waiting
- `@review` - Needs thinking

**References:**

- `[Project-Name]` - Links to project folder
- `[A-Area-Name]` - Links to area
</gtd_tasks_format>

<project_structure>

## Project Structure

**Single-file project:**

```
1 Projects/
└── Project-Name.md
```

**Multi-file project:**

```
1 Projects/
└── Project-Name/
    ├── README.md           # Project definition
    ├── notes.md            # Working notes
    ├── research/           # Research materials
    └── deliverables/       # Output files
```

**Project file template:**

```markdown
# [Project Name]

## Outcome
**What:** [Specific deliverable]
**Why:** [Business value]
**Success Criteria:** [How to know it's done]
**Timeline:** [Deadline or duration]

## Next Actions
- [ ] First next action @context

## Resources
- [[Related-Area]]
- [[Related-Resource]]

## Notes
[Project-specific notes]
```

</project_structure>

<metadata_files>

## Metadata Files (.claude/metadata/)

**review.json** - Review tracking:

```json
{
  "last_reviews": {
    "daily": "2024-01-15T09:00:00Z",
    "weekly": "2024-01-14T10:00:00Z",
    "monthly": "2024-01-01T10:00:00Z"
  }
}
```

**graph.json** - Knowledge graph metrics:

```json
{
  "total_concepts": 127,
  "total_connections": 289,
  "orphaned_notes": 3,
  "hub_concepts": [...]
}
```

**capture.json** - Capture settings:

```json
{
  "auto_categorize": true,
  "work_hours": {
    "start": "09:00",
    "end": "18:00"
  }
}
```

</metadata_files>

<naming_conventions>

## Naming Conventions

**Folders:**

- PARA folders: Numbered prefix (`1 Projects/`, `2 Areas/`)
- Projects: Title-Case-With-Hyphens
- Resources: kebab-case or Title-Case by preference

**Files:**

- Index files: `_INDEX.md` (underscore prefix for sorting)
- GTD tasks: `_GTD_TASKS.md`
- Zettelkasten: `YYYYMMDD-concept-name.md`
- General notes: `kebab-case.md` or `Title Case.md`

**Links:**

- Obsidian wiki-links: `[[Note Name]]`
- With alias: `[[Note Name|Display Text]]`
</naming_conventions>

<obsidian_integration>

## Obsidian-Specific Features

**Plugins used:**

- Tasks - Task management
- Dataview - Queries and dashboards
- Templater - Note templates
- QuickAdd - Rapid capture
- Calendar - Date navigation

**Graph view:**

- Zettelkasten connections visible in Obsidian's graph
- Local graph shows immediate connections
- Good for discovering clusters

**Backlinks:**

- See all notes linking to current note
- Essential for Zettelkasten navigation
- Enable "Backlinks in document" for inline view
</obsidian_integration>
