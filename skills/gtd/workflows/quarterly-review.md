# Quarterly Review Workflow

**Cadence:** Every 3 months
**Duration:** ~1 hour

## Purpose

Step back from day-to-day execution to assess progress on goals, evaluate project alignment, and set focus for the next quarter.

## Horizon Tracking Reference

| Horizon | Where | During Quarterly Review |
|---------|-------|------------------------|
| H1 (Projects) | GTD projects (`horizon/project`) | Check progress, close completed |
| H2 (Areas) | `2_Areas/` folder in vault | Check balance across areas |
| H3 (Goals) | GTD items (`horizon/goal`) | Review progress, adjust if needed |

**Key distinction:**

- H1/H3 are **trackable GTD items** — you can measure progress and close them
- H2 (Areas) are **vault folders** — you check balance, not completion

## Steps

### 1. Review Goals (H3)

List your 1-2 year goals:

```bash
$GTD list --horizon goal
```

For each goal, ask:

- Am I making progress?
- Is this still important to me?
- Do I need to adjust the goal?

**Note:** If empty, consider creating trackable goals from your HORIZONS.md vision.

### 2. Review Projects (H1)

Check alignment between projects and goals:

```bash
$GTD projects
$GTD list --horizon project
```

Ask:

- Which projects support my goals?
- Are there projects without clear goal alignment?
- Should I close any completed or abandoned projects?

### 3. Review Project Progress

Check completion rates:

```bash
$GTD project show "Project Name"
```

Celebrate progress. Identify stalled projects.

### 4. Review Areas of Focus (H2 — Vault Folders)

Glance at your `2_Areas/` folder:

```bash
ls 2\ Areas/
```

Ask:

- Am I spending time in all important areas?
- Is any area being neglected?
- Do my active projects align with my areas?

### 5. Clean Up Someday/Maybe

Review items that have been dormant:

```bash
$GTD list --status someday
```

Actions:

- **Activate:** `$GTD update <id> --status active`
- **Delete:** `$GTD done <id>` (or close if truly dead)
- **Keep:** Leave in someday for future review

### 6. Reflection Questions

Take time to honestly answer:

- What did I accomplish this quarter?
- What didn't get done? Why?
- What do I want to focus on next quarter?
- Are my goals still aligned with my vision?
- What's one thing I should stop doing?
- What's one thing I should start doing?

### 7. Set Next Quarter Focus

Choose 1-3 key themes or objectives for the next quarter.

**If you need a new goal (trackable):**

```bash
$GTD add "Q2 2026: Focus theme" --horizon goal
```

**If you need a new project to achieve a goal:**

```bash
$GTD add "Project name" --horizon project
```

## Completion

Running `gtd quarterly` automatically marks the quarterly review as complete.

## Connection to Other Horizons

The quarterly review bridges:

- **Down:** Ensures projects (H1) are executing toward goals (H3)
- **Up:** Checks goals (H3) align with Areas (H2) and Vision (H4 in HORIZONS.md)

If you find your goals drifting from your vision, consider a mini yearly review to realign HORIZONS.md.
