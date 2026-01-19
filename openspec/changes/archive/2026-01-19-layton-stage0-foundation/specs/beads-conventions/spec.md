# Beads Conventions Specification

How Layton uses Beads (`bd` CLI) for state management. Layton does NOT wrap Beads - it uses `bd` directly with defined conventions.

**References:**

- [Beads CLI Reference](/Users/mhild/src/durandom/agentic/task_tracking/beads/docs/CLI_REFERENCE.md)
- [Writing Skills Recipe](../../../recipes/writing-skills.md) — Skill authoring best practices

## ADDED Requirements

### Requirement: Beads as primary state store

Layton SHALL use Beads for all mutable state management.

#### Scenario: No custom state files

- **WHEN** Layton needs to track state
- **THEN** it SHALL use Beads (`.beads/`) NOT custom files like `.layton/state.json`

#### Scenario: Config is not state

- **WHEN** Layton stores personal configuration
- **THEN** it SHALL use `.layton/config.json` (stable settings, not mutable state)

---

### Requirement: Tag conventions for Layton beads

Layton SHALL use simple labels (not `bd state`) for Stage 0. State machine pattern MAY be adopted in future stages.

#### Scenario: Watching label for attention items

- **WHEN** user asks Layton to track an item
- **THEN** SKILL.md SHALL create bead with label `watching`
- **AND** example: `bd create "JIRA-1234: blocking release" -t task -p 2 -l watching,layton --json`

#### Scenario: Focus label for current work

- **WHEN** user sets current focus
- **THEN** SKILL.md SHALL create/update bead with label `focus`
- **AND** only ONE bead SHOULD have `focus` label at a time
- **AND** previous focus bead SHOULD have `focus` label removed

#### Scenario: Layton namespace label

- **WHEN** Layton creates any bead
- **THEN** bead SHALL include label `layton` for filtering
- **AND** example: `bd list --label layton --json`

#### Scenario: Source system labels

- **WHEN** tracking an item from an external system (Jira, GitHub, etc.)
- **THEN** bead SHOULD include system-specific label
- **AND** example: `bd create "..." -t task -p 2 -l watching,jira,layton --json`

---

### Requirement: Bead description conventions

Bead descriptions SHALL follow a consistent format for AI parsing.

#### Scenario: External reference format

- **WHEN** tracking an external item
- **THEN** description SHALL start with system ID
- **AND** example: `"JIRA-1234: blocking release - promised Kim to check Monday"`

#### Scenario: Context after colon

- **WHEN** bead has user context
- **THEN** context SHALL follow the ID after a colon separator
- **AND** this allows splitting ID from annotation

---

### Requirement: Querying Layton beads

SKILL.md workflows SHALL query beads using standard `bd` commands with `--json` flag.

#### Scenario: List watched items

- **WHEN** SKILL.md needs attention items
- **THEN** it SHALL run `bd list --label watching --json`

#### Scenario: List current focus

- **WHEN** SKILL.md needs current focus
- **THEN** it SHALL run `bd list --label focus --json`

#### Scenario: List all Layton beads

- **WHEN** SKILL.md needs all Layton-managed beads
- **THEN** it SHALL run `bd list --label layton --json`

#### Scenario: Check ready work

- **WHEN** SKILL.md needs unblocked tasks
- **THEN** it SHALL run `bd ready --json`

---

### Requirement: Beads availability check

`layton doctor` SHALL verify Beads is available.

#### Scenario: bd CLI in PATH

- **WHEN** `bd info --json` succeeds
- **THEN** `beads_available` check SHALL pass

#### Scenario: bd CLI missing

- **WHEN** `bd` command is not found
- **THEN** `beads_available` check SHALL fail
- **AND** status SHALL be `"fail"` (critical, not fixable by Layton)

#### Scenario: beads not initialized

- **WHEN** `bd` is available but `.beads/` directory does not exist
- **THEN** doctor SHALL warn but not fail
- **AND** `next_steps` SHALL suggest `bd init`

---

### Requirement: SKILL.md direct Beads usage

SKILL.md workflows SHALL invoke `bd` directly, not via Layton CLI.

#### Scenario: No layton track command

- **WHEN** user asks to track something
- **THEN** SKILL.md SHALL call `bd create ... -l watching,layton --json` directly
- **AND** Layton CLI SHALL NOT have `track`, `untrack`, or `watched` commands

#### Scenario: SKILL.md reads beads for synthesis

- **WHEN** generating morning briefing
- **THEN** SKILL.md SHALL combine:
  - `bd list --label watching --json` (attention items)
  - `bd list --label focus --json` (current focus)
  - `layton context` (temporal context — JSON by default)

#### Scenario: Closing tracked items

- **WHEN** user says "stop tracking X" or "that's done"
- **THEN** SKILL.md SHALL call `bd close <id> --reason "..." --json`

---

## Skill Implementation Guide

This section defines how to structure SKILL.md and related files so Claude can effectively use Beads. Follow the [Writing Skills Recipe](../../../recipes/writing-skills.md) for general skill authoring best practices.

### Requirement: Skill directory structure (Router Pattern)

The Layton skill SHALL use the Router Pattern for multi-workflow organization.

#### Scenario: Directory layout

- **WHEN** organizing the Layton skill
- **THEN** directory structure SHALL be:

```
skills/layton/
├── SKILL.md              # Router + essential principles (under 500 lines)
├── workflows/            # Step-by-step procedures (FOLLOW)
│   ├── morning-briefing.md
│   ├── track-item.md
│   └── set-focus.md
├── references/           # Domain knowledge (READ on-demand)
│   ├── beads-commands.md
│   └── persona.md
└── scripts/              # Executable code (RUN)
    └── layton            # CLI entrypoint
```

#### Scenario: SKILL.md as router

- **WHEN** user invokes Layton
- **THEN** SKILL.md SHALL route to appropriate workflow
- **AND** SKILL.md SHALL NOT contain verbose command documentation
- **AND** detailed bd commands go in `references/beads-commands.md`

---

### Requirement: Pure XML structure in SKILL.md

SKILL.md body SHALL use semantic XML tags, not markdown headings. This follows the Writing Skills Recipe principle of pure XML structure.

#### Scenario: Required XML tags

- **WHEN** structuring SKILL.md body
- **THEN** it SHALL include these required tags:
  - `<objective>` — What Layton does
  - `<quick_start>` — Immediate actionable guidance
  - `<success_criteria>` — How to know it worked

#### Scenario: Example SKILL.md structure

```xml
---
name: layton
description: Personal AI assistant for attention management. Use when user asks about focus, briefings, or tracking items across systems.
---

<objective>
Layton is your personal secretary—managing attention, synthesizing information from multiple systems, and providing context-aware briefings.
</objective>

<quick_start>
**Morning briefing**: Run workflow in `workflows/morning-briefing.md`
**Track something**: Run workflow in `workflows/track-item.md`
**Set focus**: Run workflow in `workflows/set-focus.md`

For bd command details, see `references/beads-commands.md`.
</quick_start>

<principles>
- Use `bd` directly for all state operations (never wrap it)
- Always include `--json` flag for machine-readable output
- Always include `layton` label on beads Layton creates
</principles>

<success_criteria>
- [ ] User knows what they're tracking
- [ ] User knows their current focus
- [ ] Briefings adapt to time of day and workload
</success_criteria>
```

---

### Requirement: Degrees of freedom for bd commands

Beads commands are **LOW FREEDOM** operations—exact syntax matters.

#### Scenario: Low freedom rationale

- **WHEN** documenting bd commands
- **THEN** spec SHALL treat them as fragile operations
- **AND** workflows SHALL specify exact commands (not "use bd to create...")
- **AND** flags SHALL be explicit (not "add appropriate labels")

#### Scenario: Low freedom example

```xml
<!-- BAD: High freedom, vague -->
<step>Create a bead to track the item with appropriate labels.</step>

<!-- GOOD: Low freedom, exact -->
<step>
Create bead:
`bd create "<ID>: <context>" -t task -p 2 -l watching,<source>,layton --json`
</step>
```

---

### Requirement: Workflow file structure

Workflow files in `workflows/` SHALL use XML structure with numbered steps.

#### Scenario: Track item workflow

- **WHEN** creating `workflows/track-item.md`
- **THEN** it SHALL be structured as:

```xml
<workflow name="track-item">
<objective>Add an item to Layton's attention list.</objective>

<steps>
1. Parse user request for: item ID, source system, context
2. Create bead:
   `bd create "<ID>: <context>" -t task -p 2 -l watching,<source>,layton --json`
3. Confirm to user with bead ID for future reference
</steps>

<success_criteria>
- [ ] Bead created with `watching` and `layton` labels
- [ ] User received confirmation with bead ID
</success_criteria>
</workflow>
```

#### Scenario: Morning briefing workflow

- **WHEN** creating `workflows/morning-briefing.md`
- **THEN** it SHALL be structured as:

```xml
<workflow name="morning-briefing">
<objective>Provide context-aware status update.</objective>

<steps>
1. Get temporal context: `layton context`
2. Get attention items: `bd list --label watching --json`
3. Get current focus: `bd list --label focus --json`
4. Synthesize briefing using persona voice (see `references/persona.md`)
</steps>

<synthesis_rules>
Order of presentation:
1. Current focus (if any) — "You're working on..."
2. Attention items sorted by priority — "Watching N items..."
3. Time-appropriate suggestions — based on `time_of_day`

Context adaptation:
- `morning` + `work_hours: true` → full briefing
- `evening` + `work_hours: false` → brief summary only
- attention count > 5 → suggest triage
</synthesis_rules>

<success_criteria>
- [ ] Briefing adapts to time of day
- [ ] Focus item mentioned first (if exists)
- [ ] Attention items summarized with counts
</success_criteria>
</workflow>
```

#### Scenario: Set focus workflow

- **WHEN** creating `workflows/set-focus.md`
- **THEN** it SHALL handle single-focus constraint:

```xml
<workflow name="set-focus">
<objective>Set current focus (only one at a time).</objective>

<steps>
1. Check existing focus: `bd list --label focus --json`
2. If focus exists, remove label: `bd update <old-id> --remove-label focus --json`
3. Set new focus:
   - Existing bead: `bd update <id> --add-label focus --json`
   - New item: `bd create "<description>" -t task -p 2 -l focus,layton --json`
</steps>

<success_criteria>
- [ ] Only ONE bead has `focus` label
- [ ] Previous focus label removed (if any)
</success_criteria>
</workflow>
```

---

### Requirement: Reference file structure

The skill SHALL include a `references/beads-commands.md` file for detailed bd usage.

#### Scenario: Beads command reference content

- **WHEN** creating `references/beads-commands.md`
- **THEN** it SHALL be concise (assume Claude knows bd basics)
- **AND** it SHALL include sections for:
  - Creating beads (with label conventions)
  - Querying beads (list, ready, show)
  - Updating beads (labels, status)
  - Closing beads
- **AND** each section SHALL show JSON output schema

#### Scenario: Conciseness in reference files

- **WHEN** writing reference files
- **THEN** do NOT explain what bd is or how CLIs work
- **AND** do NOT include tutorial-style explanations
- **AND** DO include exact command syntax and output schemas

#### Scenario: Example beads-commands.md structure

```markdown
# Beads Command Reference

## Creating beads

**Track external item:**
`bd create "JIRA-1234: blocking release" -t task -p 2 -l watching,jira,layton --json`

Output:
```json
{"id": "beads-abc", "title": "JIRA-1234: blocking release", "labels": ["watching", "jira", "layton"]}
```

## Querying beads

| Query | Command |
|-------|---------|
| Watched items | `bd list --label watching --json` |
| Current focus | `bd list --label focus --json` |
| All Layton beads | `bd list --label layton --json` |
| Ready work | `bd ready --json` |

## Updating beads

**Add label:** `bd update <id> --add-label <label> --json`
**Remove label:** `bd update <id> --remove-label <label> --json`

## Closing beads

`bd close <id> --reason "..." --json`

```
