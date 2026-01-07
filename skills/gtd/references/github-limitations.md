<overview>
GitHub Issues provides a solid foundation for GTD, but some GTD concepts don't map directly. This document explains the gaps and provides workarounds.

**TL;DR**: Most GTD concepts work well with labels and milestones. For advanced features (due dates, dependencies, recurring tasks), use conventions documented below.
</overview>

<concept_mapping>

## GTD Concepts → GitHub Mapping

| GTD Concept | GitHub Feature | Works Well? |
|-------------|----------------|-------------|
| Actions/Tasks | Issues | ✅ Yes |
| Projects | Milestones | ✅ Yes |
| Contexts | Labels (context/*) | ✅ Yes |
| Status | Labels (status/*) | ✅ Yes |
| Energy | Labels (energy/*) | ✅ Yes |
| Horizons | Labels (horizon/*) | ✅ Yes |
| Due Dates | Issue body convention | ⚠️ Workaround |
| Dependencies | Issue links + convention | ⚠️ Workaround |
| Waiting-For | status/waiting + @mention | ⚠️ Workaround |
| Recurring Tasks | GitHub Actions | ⚠️ Workaround |
| Someday/Maybe | status/someday label | ✅ Yes |

</concept_mapping>

<due_dates>

## Due Dates

**The Gap**: GitHub only supports due dates at the milestone level, not individual issues.

**Workaround**: Use a convention in the issue body or title.

### Option 1: Body Convention

Add a line at the top of the issue body:

```
Due: 2026-01-15
```

### Option 2: Title Suffix

Add the date to the title:

```
Review quarterly report [Due: 2026-01-15]
```

### Option 3: GitHub Projects (Advanced)

GitHub Projects (the new Projects, not classic) supports custom date fields.

```bash
# List project fields
gh project field-list --owner <owner> <project-number>

# Set a date field (requires project item ID)
gh project item-edit --project-id <id> --field-id <field-id> --date 2026-01-15
```

**Note**: The `gh project` commands are more complex than issue commands. For simple GTD use, the body convention is recommended.

### Filtering by Due Date

With the body convention, you can grep for upcoming items:

```bash
gh issue list --json number,title,body | \
  jq -r '.[] | select(.body | contains("Due: 2026-01"))'
```

</due_dates>

<dependencies>

## Issue Dependencies

**The Gap**: GitHub has "linked issues" but no true dependency graph or blocking mechanism.

**Workaround**: Use conventions in the issue body.

### Convention: Blocked By

Add to the issue body:

```
Blocked by: #123, #124
```

### Convention: Blocks

Add to the issue body:

```
Blocks: #125
```

### GTD Mapping

In GTD terms:

- If an action is blocked, set `status/waiting`
- The issue body documents what you're waiting for
- When the blocker is resolved, change to `status/active`

### Example Workflow

```bash
# Task is blocked by #42
gtd update 50 --status waiting
gh issue comment 50 --body "Blocked by: #42 (waiting for API spec)"

# Later, when #42 is done
gtd update 50 --status active
gh issue comment 50 --body "Unblocked: #42 resolved"
```

### Automated Checking (Future Enhancement)

A GitHub Action could scan for `Blocked by:` patterns and auto-update status when blockers close.

</dependencies>

<waiting_for>

## Waiting-For Tracking

**The Gap**: GTD's "Waiting For" context tracks *who* you're waiting on, not just that you're waiting.

**Workaround**: Combine `status/waiting` with @mentions in comments.

### Convention

When marking something as waiting:

```bash
gtd update 36 --status waiting
gtd comment 36 "Waiting for: @alice to review the PR"
```

### Viewing Waiting Items

```bash
# List all waiting items
gtd list --status waiting

# Search for who you're waiting on
gh issue list --label status/waiting --json number,title,body | \
  jq -r '.[] | select(.body | contains("@alice"))'
```

### Best Practice

Always document:

1. Who you're waiting for (@mention)
2. What you're waiting for (specific deliverable)
3. When you started waiting (automatic via comment timestamp)

</waiting_for>

<recurring_tasks>

## Recurring Tasks

**The Gap**: GitHub has no built-in recurring task support.

**Workaround**: Use GitHub Actions to auto-create issues on a schedule.

### GitHub Action for Recurring Tasks

Create `.github/workflows/recurring-tasks.yml`:

```yaml
name: Recurring GTD Tasks

on:
  schedule:
    # Every Monday at 9am UTC
    - cron: '0 9 * * 1'

jobs:
  create-weekly-review:
    runs-on: ubuntu-latest
    steps:
      - name: Create weekly review task
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Weekly Review',
              body: 'Time for your weekly review!\n\nRun: `gtd weekly`',
              labels: ['status/active', 'context/focus', 'energy/low', 'horizon/action']
            })
```

### Common Recurring Patterns

| Task | Cron Schedule |
|------|---------------|
| Weekly Review | `0 9 * * 1` (Monday 9am) |
| Monthly Review | `0 9 1 * *` (1st of month) |
| Daily Standup Prep | `0 8 * * 1-5` (Weekdays 8am) |
| Quarterly Goals | `0 9 1 1,4,7,10 *` (Jan/Apr/Jul/Oct 1st) |

### Alternative: External Reminder

Use a calendar or reminder app to prompt you to run:

```bash
gtd add "Weekly review" --context focus --energy low --status active
```

</recurring_tasks>

<someday_maybe>

## Someday/Maybe vs Active

**The Gap**: GTD distinguishes "someday/maybe" (not committed) from "active" (committed). GitHub doesn't have a native "hide from view" feature.

**Solution**: The `status/someday` label handles this well.

### How It Works

- `status/someday`: Items you might do eventually, not committed
- `status/active`: Items you're committed to doing
- Items without status: Inbox (unclarified)

### Hiding from Daily View

The `gtd daily` and `gtd next` commands only show `status/active` items, so someday/maybe items are naturally hidden.

```bash
# This shows only active items
gtd daily

# To review someday/maybe (weekly or quarterly)
gtd list --status someday
```

### Promoting Someday to Active

During weekly review, decide if any someday items should become active:

```bash
gtd update 42 --status active
```

### Tickler/Defer Pattern

If you want to defer something until a future date:

1. Keep it as `status/someday`
2. Add a convention to the body: `Defer until: 2026-03-01`
3. During reviews, check deferred items and promote if the date has passed

</someday_maybe>

<projects_advanced>

## GitHub Projects Integration (Advanced)

GitHub Projects (the new version) offers additional fields that could enhance GTD:

### Available Custom Fields

- **Date fields**: For due dates
- **Number fields**: For priority scores
- **Single select**: For custom statuses
- **Iteration fields**: For sprints/cycles

### Accessing via CLI

```bash
# List your projects
gh project list

# View project items
gh project item-list <project-number> --owner <owner>
```

### Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Labels only | Simple, fast, CLI-friendly | Limited date support |
| Labels + Projects | Rich fields, Kanban view | More complex, slower queries |

**Recommendation**: Start with labels only. Add Projects integration if you need:

- Due date filtering
- Kanban board visualization
- Sprint/iteration planning

</projects_advanced>

<conventions_summary>

## Quick Reference: Conventions

### Issue Body Conventions

```markdown
Due: 2026-01-15
Blocked by: #123, #124
Blocks: #125
Waiting for: @alice to review
Defer until: 2026-03-01
```

### Parsing Conventions with jq

```bash
# Find issues due this month
gh issue list --json number,title,body | \
  jq -r '.[] | select(.body | test("Due: 2026-01"))'

# Find issues blocked by #123
gh issue list --json number,title,body | \
  jq -r '.[] | select(.body | contains("Blocked by: #123"))'

# Find issues waiting on @alice
gh issue list --label status/waiting --json number,title,body | \
  jq -r '.[] | select(.body | contains("@alice"))'
```

</conventions_summary>

<future_enhancements>

## Potential Future Enhancements

1. **`gtd defer <id> <date>`**: Add defer-until convention and auto-promote
2. **`gtd blocked <id> <blocker-ids>`**: Add blocked-by convention
3. **`gtd waiting <id> @person "reason"`**: Structured waiting-for tracking
4. **Due date parsing**: Add `--due-before` filter to `gtd list`
5. **GitHub Projects integration**: Add `--project-field` options

See GitHub issue #5 for discussion and contributions.

</future_enhancements>
