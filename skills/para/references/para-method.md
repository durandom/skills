# PARA Method Reference

## Core Principle: Actionability Over Topic

Traditional filing organizes by subject ("JavaScript", "Finance"). PARA organizes by **when and how you'll use the information**:

| Category | Question It Answers | Timeframe |
|----------|---------------------|-----------|
| Projects | What am I working on? | Days to weeks |
| Areas | What do I maintain? | Ongoing |
| Resources | What might I need? | Someday |
| Archive | What did I finish? | Historical |

## The Four Categories

### Projects

**Definition:** A series of tasks linked to a specific goal with a deadline.

**Characteristics:**

- Clear, achievable outcome
- Defined timeline (even if approximate)
- Can be "completed" and archived
- Contains all materials needed for progress

**Examples:**

- `API-Redesign-v2/` - Active development
- `Security-Audit-Q4/` - Time-bound audit
- `Conference-Talk-March/` - Specific deliverable

**Language signals:** "complete", "deliver", "launch", "finish", "ship"

### Areas

**Definition:** Spheres of responsibility requiring ongoing maintenance, no end date.

**Characteristics:**

- Never "complete"
- Represents a role or responsibility
- Has standards to maintain
- Source of new projects

**Examples:**

- `Engineering-Management.md` - Leadership responsibility
- `Personal-Finance.md` - Life maintenance
- `Health-Fitness.md` - Continuous standard

**Language signals:** "maintain", "manage", "oversee", "track", "monitor"

**Project vs Area:**

- You don't "complete" your health—you maintain it (Area)
- You can complete "Run a 5K race" (Project born from Area)

### Resources

**Definition:** Topics of interest not tied to active projects or responsibilities.

**Characteristics:**

- No responsibility attached
- Reference material for potential future use
- Organized by topic/interest
- Can feed into projects when needed

**Examples:**

- `kubernetes/` - Learning materials
- `system-design-patterns/` - Architectural knowledge
- `interview-prep/` - Reference collection

**Language signals:** "interesting", "might need", "good to know", "for reference"

**Warning:** Resources can become a dumping ground. Review periodically.

### Archive

**Definition:** Inactive items from the other three categories.

**Characteristics:**

- "Cold storage" for completed/paused work
- Preserves context and history
- Searchable when needed
- Not deleted—just out of sight

**When to archive:**

- Project completed or abandoned
- Area of responsibility ended (role change)
- Resource no longer of interest

## Just-in-Time Organization

**DO:**

- Create folders when you have something to put in them
- Let structure emerge from actual work
- Move items between categories as status changes
- Archive aggressively to keep active view clean

**DON'T:**

- Pre-create elaborate folder hierarchies
- Spend more time organizing than working
- Create empty placeholder folders
- Treat category assignments as permanent

## GTD Integration

PARA provides the **filing cabinet**; GTD provides the **workflow**:

| System | Handles | Storage |
|--------|---------|---------|
| GTD | Task tracking, next actions | GitHub issues/milestones |
| PARA | Notes, documentation, files | Filesystem folders |

**Sync requirement:** GTD projects (milestones) and PARA projects (folders) share names and stay in sync. When you create a GTD project, create the matching PARA folder. When you archive a GTD project, archive the PARA folder.
