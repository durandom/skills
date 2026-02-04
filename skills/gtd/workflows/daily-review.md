# Daily Review Workflow

**Cadence:** Every day (ideally morning)
**Duration:** ~5 minutes

## Purpose

Start your day with clear priorities by reviewing what needs attention and deciding what to focus on.

## Horizon Tracking Reference

| Horizon | Where | During Daily Review |
|---------|-------|---------------------|
| Ground (Actions) | GTD items (`horizon/action`) | Filter by context/energy for today |

**Scope:** Daily review is purely tactical — focused on Ground level only. This is about picking what to work on today, not strategic planning.

## Steps

### 1. Check Deferred Items

Review items that were deferred and are now active:

```bash
$GTD daily  # Shows deferred items now active
```

Update any deferred items that are now relevant:

```bash
$GTD update <id> --status active
```

### 2. Review High-Energy Focus Work

These are your most important tasks requiring deep concentration:

```bash
$GTD list --context focus --energy high --status active
```

Choose 1-3 items to prioritize for your morning focus time.

### 3. Review Low-Energy Focus Work

Tasks requiring focus but less cognitive load:

```bash
$GTD list --context focus --energy low --status active
```

Good for afternoon or when energy dips.

### 4. Check Waiting Items

See what you're waiting on from others:

```bash
$GTD list --status waiting
```

Follow up on any items where someone hasn't responded.

### 5. Process Inbox (if items present)

If there are items in your inbox, process at least one:

```bash
$GTD inbox
$GTD clarify <id> --status active --context <context>
```

### 6. Check Overdue Items

Review anything past due:

```bash
$GTD list --overdue
```

Reschedule, complete, or delegate overdue items.

## Completion

Running `gtd daily` automatically marks the daily review as complete.

## Output

The daily review shows:

- High energy focus work (morning)
- Light focus work
- Async work (anytime)
- Waiting on others
- Deferred items now active
- Overdue items
- Blocked items (check if blockers resolved)
- Inbox count
