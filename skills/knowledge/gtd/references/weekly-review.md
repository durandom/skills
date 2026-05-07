# Weekly Review Workflow

**Cadence:** Once per week (ideally Friday or Sunday)
**Duration:** ~15-30 minutes

## Purpose

Get your system current and complete by processing all inputs and reviewing all active commitments. This is the keystone habit of GTD — without it, the system degrades.

## Horizon Tracking Reference

| Horizon | Where | During Weekly Review |
|---------|-------|---------------------|
| Ground (Actions) | GTD items (`horizon/action`) | Review all active/waiting |
| H1 (Projects) | GTD projects (`horizon/project`) | Ensure each has next action |

**Scope:** Weekly review is tactical — focused on Ground and H1 only. For strategic horizons (H2-H5), see quarterly and yearly reviews.

## Steps

### 1. Process Inbox to Zero

Empty your inbox by clarifying every item:

```bash
$GTD inbox
```

For each item, decide:

- **Actionable?** → `$GTD clarify <id> --status active --context <ctx>`
- **Not actionable?** → `$GTD clarify <id> --not-actionable --delete|--someday|--reference`

### 2. Review Active Items

Ensure all active items are still relevant:

```bash
$GTD list --status active
```

Ask for each:

- Is this still a commitment?
- Is it correctly labeled (context, energy)?
- Should it be delegated or deferred?

### 3. Review Waiting Items

Check on items you're waiting for from others:

```bash
$GTD list --status waiting
```

Actions:

- Follow up on stale items
- Check if blockers are resolved: `$GTD blocked <id>`
- Move completed waiting items back to active

### 4. Review Projects (H1)

Ensure every project has at least one active next action:

```bash
$GTD projects
$GTD list --horizon project
```

For each project without an active action:

```bash
$GTD add "Next action for project" --project "Project Name" --status active
```

### 5. Review Someday/Maybe

Scan your someday/maybe list for items to activate or delete:

```bash
$GTD list --status someday
```

Ask:

- Do I still want to do this?
- Is now the time to activate it?
- Should I delete it?

### 6. Review Calendar (External)

Look at your calendar for the past week:

- Capture any follow-up actions
- Note any commitments made

Look at upcoming week:

- Capture any prep work needed
- Identify potential conflicts

## Completion

Running `gtd weekly` automatically marks the weekly review as complete.

## Key Principle

The weekly review is when you get your head out of the weeds and look at the bigger picture. It's not about doing work — it's about reviewing and renegotiating your commitments.
