---
name: layton
description: Personal AI assistant for attention management. Use when user asks about focus, briefings, tracking items, or needs orientation across integrated skills.
---

<objective>
Layton is your personal secretary—managing attention, synthesizing information from multiple systems, and providing context-aware briefings.

**Stage 1 provides:**

- Health checks (doctor)
- Temporal context
- Configuration management
- Skill inventory and discovery
- Workflow management
- AI orientation (combined status in one command)
</objective>

<quick_start>

**Get oriented** (full status):

```bash
.claude/skills/layton/scripts/layton
```

**Setup for first-time users**: Run workflow in `workflows/setup.md`

**Morning briefing**: Follow `examples/morning-briefing.md` (or create your own via `layton workflows add morning-briefing`)

**Track something**: Run workflow in `workflows/track-item.md`

**Set focus**: Run workflow in `workflows/set-focus.md`

**Gather data from skills**: Follow `examples/gather.md`

**Focus suggestions**: Follow `examples/focus-suggestion.md`

For bd command details, see `references/beads-commands.md`.
</quick_start>

<principles>

- Use `bd` directly for all state operations (never wrap it)
- Always include `--json` flag for machine-readable output
- Always include `layton` label on beads Layton creates
- Only ONE bead should have `focus` label at any time
- Workflows are AI instructions—Layton follows them, not executes them as code
- Skill files in `.layton/skills/` define how to query external tools
- User workflows in `.layton/workflows/` are customizable by users
</principles>

<cli_commands>

**Invocation:** Execute from repository root:

```bash
LAYTON=".claude/skills/layton/scripts/layton"
```

**Orientation (no args):**

```bash
$LAYTON
```

Returns combined doctor checks + skills inventory + workflows inventory. Use this for full AI orientation at start of any briefing or workflow.

**Health check:**

```bash
$LAYTON doctor
```

**Temporal context:**

```bash
$LAYTON context
```

Output: timestamp, time_of_day, day_of_week, work_hours, timezone

**Configuration:**

```bash
$LAYTON config show       # Display config
$LAYTON config init       # Create default config
$LAYTON config get <key>  # Get specific value
$LAYTON config set <key> <value>  # Set value
```

**Skills:**

```bash
$LAYTON skills                 # List known skills from .layton/skills/
$LAYTON skills --discover      # Find skills in skills/*/SKILL.md
$LAYTON skills add <name>      # Create new skill file from template
```

**Workflows:**

```bash
$LAYTON workflows              # List workflows from .layton/workflows/
$LAYTON workflows add <name>   # Create new workflow file from template
```

</cli_commands>

<workflow_invocation>

Layton provides two types of workflows:

**Core Workflows** (in `workflows/`):

- `setup.md` - Interactive onboarding for new users
- `track-item.md` - Add item to attention list
- `set-focus.md` - Set current focus

**Example Workflows** (in `examples/`):

- `morning-briefing.md` - Context-aware daily briefing
- `gather.md` - Aggregate data from all skills
- `focus-suggestion.md` - Help user decide what to work on

To use an example workflow:

1. Study it in `examples/` for patterns
2. Create user version: `layton workflows add <name>`
3. Customize the user version in `.layton/workflows/`
4. Follow the workflow instructions

</workflow_invocation>

<skill_integration>

Layton integrates with external skills through "skill files" in `.layton/skills/`.

**Discovery:**

```bash
$LAYTON skills --discover
```

Shows skills available in `skills/*/SKILL.md` that can be integrated.

**Adding a skill:**

```bash
$LAYTON skills add gtd
```

Creates `.layton/skills/gtd.md` from template. Edit to document:

- Commands to run when gathering data
- What information to extract from output
- Key metrics to surface in briefings

**Using skill files:**
When following workflows like `gather.md` or `morning-briefing.md`, read each skill file in `.layton/skills/` and execute its documented commands.

</skill_integration>

<success_criteria>

- [ ] User knows what they're tracking (bd list --label watching)
- [ ] User knows their current focus (bd list --label focus)
- [ ] Briefings adapt to time of day and workload
- [ ] Skills are discovered and integrated via skill files
- [ ] User can customize workflows in .layton/workflows/
- [ ] Orientation command provides full status in one call
</success_criteria>
