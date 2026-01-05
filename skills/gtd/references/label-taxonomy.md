# GTD Label Taxonomy

Complete reference for the 6-dimensional label system.

**⚠️ CRITICAL: This is a CLOSED taxonomy - do NOT create new labels!**

- The 26 labels below are the complete, fixed set
- If you need a label that doesn't exist, choose the closest existing one
- If truly uncertain, ASK THE USER before creating anything

## Context Labels (Work Mode)

Based on actual work patterns - how you choose what to work on:

- `context/focus` - Morning deep work (8am-1pm): architecture, design, writing
- `context/meetings` - Afternoon synchronous (2-6pm): calls, live collaboration
- `context/async` - Asynchronous: Slack threads, Google Docs, JIRA comments
- `context/offsite` - Quarterly travel: customer visits, team offsites

**Usage:** Filter by current time/mode

```bash
# Morning: What can I do in my focus block?
gh issue list --label "context/focus" --label "horizon/now"

# Afternoon: What's between meetings?
gh issue list --label "context/async" --label "horizon/now"

# Before travel: What needs prep?
gh issue list --label "context/offsite"
```

**Combinations:** Issues can have multiple contexts if they fit different modes

- `context/focus` + `context/async` = Can do in focus time OR asynchronously
- `context/offsite` + `context/focus` = Travel prep that needs deep thinking

## Energy Labels (Cognitive Load)

Not about time, but about mental overhead required:

- `energy/high` - Needs context, preparation, deep thinking
- `energy/low` - Quick, routine, low mental overhead (admin, Workday)

**Usage:** Match task to current energy level

```bash
# Morning when fresh: Show heavy lifting
gh issue list --label "context/focus" --label "energy/high"

# Between meetings when fragmented: Show light tasks
gh issue list --label "context/async" --label "energy/low"

# End of day, low energy: What's quick?
gh issue list --label "energy/low" --state open
```

**Why separate from priority:**

- Priority = urgency/importance
- Energy = mental effort required
- They're independent: urgent admin task = `priority/high` + `energy/low`

**Examples:**

- `energy/high`: Design plugin architecture, write RFE, complex JIRA epic breakdown
- `energy/low`: Approve PR, update JIRA status, quick Slack reply, Workday entries

## Horizon Labels (GTD Time)

- `horizon/now` - Next actions (this week)
- `horizon/soon` - Upcoming (this month)
- `horizon/later` - Someday/maybe
- `horizon/waiting` - Waiting for others

**Usage:** Plan weekly work, defer non-urgent tasks

```bash
# Weekly planning
gh issue list --label "horizon/now,horizon/soon" --state open
```

## Area Labels (PARA-aligned)

- `area/career` - Career development, quarterly reviews
- `area/architecture` - Technical architecture work
- `area/plugins` - Plugin ecosystem work
- `area/customers` - Customer engagements (Ford, Citi)
- `area/ai-tooling` - AI initiatives (Sidekick, etc.)
- `area/documentation` - Documentation projects
- `area/team` - Team leadership, mentorship
- `area/process` - Engineering processes, release mgmt

**Usage:** Group work by responsibility area

```bash
# What's happening in the plugins area?
gh issue list --label "area/plugins" --state open
```

## Priority Labels

- `priority/urgent` - 🔥 Must do this week
- `priority/high` - Important, schedule soon
- `priority/normal` - Regular priority
- `priority/low` - Nice to have

**Usage:** Focus on high-impact work

```bash
# Show only urgent/high priority
gh issue list --label "priority/urgent,priority/high"
```

## Type Labels

- `type/project` - Multi-step project (epic-level)
- `type/task` - Single actionable task
- `type/achievement` - Completed work worth tracking for career
- `type/blocked` - Can't proceed, needs unblocking

**Usage:** Filter by work type, extract achievements

```bash
# Show all achievements for Q4 career review
gh issue list --label "type/achievement" --milestone "Q4-2025" --state all
```

## Powerful Label Combinations

**Morning deep work:**

```bash
gh issue list --label "context/focus,energy/high,horizon/now"
```

**Quick tasks between meetings:**

```bash
gh issue list --label "context/async,energy/low"
```

**Offsite preparation:**

```bash
gh issue list --label "context/offsite"
```

**This week's priorities:**

```bash
gh issue list --label "horizon/now,priority/high"
```

**Career achievements:**

```bash
gh issue list --label "type/achievement" --milestone "Q4-2025"
```
