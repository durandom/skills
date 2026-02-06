<critical_rule>
This is a CLOSED taxonomy - do NOT create new labels!

- The 12 labels below are the complete, fixed set
- If you need a label that doesn't exist, choose the closest existing one
- If truly uncertain, ASK THE USER before creating anything
</critical_rule>

<context_labels>

## Context Labels (Work Mode)

Based on actual work patterns - how you choose what to work on:

- `context/focus` - Morning deep work (8am-1pm): architecture, design, writing
- `context/meetings` - Afternoon synchronous (2-6pm): calls, live collaboration
- `context/async` - Asynchronous: Slack threads, Google Docs comments
- `context/offsite` - Quarterly travel: customer visits, team offsites

**Usage:** Filter by current time/mode

```bash
# Morning: What can I do in my focus block?
./gtd list --context focus --status active

# Afternoon: What's between meetings?
./gtd list --context async --status active

# Before travel: What needs prep?
./gtd list --context offsite
```

**Combinations:** Issues can have multiple contexts if they fit different modes

- `context/focus` + `context/async` = Can do in focus time OR asynchronously
- `context/offsite` + `context/focus` = Travel prep that needs deep thinking
</context_labels>

<energy_labels>

## Energy Labels (Cognitive Load)

Not about time, but about mental overhead required:

- `energy/high` - Needs context, preparation, deep thinking
- `energy/low` - Quick, routine, low mental overhead (admin, Workday)

**Usage:** Match task to current energy level

```bash
# Morning when fresh: Show heavy lifting
./gtd list --context focus --energy high

# Between meetings when fragmented: Show light tasks
./gtd list --context async --energy low

# End of day, low energy: What's quick?
./gtd list --energy low
```

**Why separate from status:**

- Status = state in workflow (ready, blocked, deferred)
- Energy = mental effort required
- They're independent: ready admin task = `status/active` + `energy/low`

**Examples:**

- `energy/high`: Design plugin architecture, write RFE, complex epic breakdown
- `energy/low`: Approve PR, update issue status, quick Slack reply, Workday entries
</energy_labels>

<status_labels>

## Status Labels (GTD Workflow State)

Where the item is in your GTD workflow:

- `status/active` - Next action, ready to work on
- `status/waiting` - Blocked on someone else, delegated
- `status/someday` - Not committed, maybe later (also used for inbox/unclarified)

**Usage:** Plan weekly work, track blocked items

```bash
# What can I work on right now?
./gtd list --status active

# What am I waiting for?
./gtd list --status waiting

# Weekly review: check someday/maybe
./gtd list --status someday
```

**Note:** These replace the old `horizon/now`, `horizon/soon`, `horizon/later`, `horizon/waiting` labels. The key insight is that GTD doesn't use "soon" - something is either actionable now or it's someday/maybe.
</status_labels>

<horizon_labels>

## Horizon Labels (GTD Altitude)

What *level* of commitment this represents (from David Allen's 6 Horizons of Focus):

- `horizon/action` - Ground level: single next physical action
- `horizon/project` - H1: multi-action outcome (1-12 months)
- `horizon/goal` - H3: 1-2 year objective

**Usage:** Distinguish actions from projects from goals

```bash
# What are my current projects?
./gtd list --horizon project

# What goals am I working toward?
./gtd list --horizon goal

# What's the next action for a project?
./gtd list --horizon action --project "Launch sidekick MVP"
```

**Higher horizons (H2, H4, H5):** Areas of Focus, Vision, and Purpose are documented in `horizons.md`, not tracked as labels. They're reviewed quarterly/yearly, not daily.

**Projects:**

When you create a `horizon/project` item, a project grouping is auto-created. Actions belonging to that project get the project assigned:

```bash
# Create a project (outcome-focused name)
./gtd add "Launch sidekick MVP" --horizon project

# Add actions to the project
./gtd add "Write user documentation" --horizon action --project "Launch sidekick MVP"
```

</horizon_labels>

<combinations>

## Powerful Label Combinations

**Morning deep work:**

```bash
./gtd list --context focus --energy high --status active
```

**Quick tasks between meetings:**

```bash
./gtd list --context async --energy low --status active
```

**Offsite preparation:**

```bash
./gtd list --context offsite --status active
```

**Weekly review - check waiting items:**

```bash
./gtd list --status waiting
```

**Quarterly review - check projects:**

```bash
./gtd projects
```

</combinations>

<label_summary>

## Complete Label List (12 labels)

| Dimension | Labels |
|-----------|--------|
| Context | focus, meetings, async, offsite |
| Energy | high, low |
| Status | active, waiting, someday |
| Horizon | action, project, goal |

</label_summary>
