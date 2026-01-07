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
| Due Dates | `gtd due` command | ✅ CLI supported |
| Defer/Tickler | `gtd defer` command | ✅ CLI supported |
| Dependencies | `gtd blocked` command | ✅ CLI supported |
| Waiting-For | `gtd waiting` command | ✅ CLI supported |
| Recurring Tasks | Labels or milestone | ⚠️ Manual |
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

**Native Support**: GitHub has native `blockedBy` and `blocking` fields accessible via GraphQL API. It also supports sub-issues and parent/child relationships.

### Available Fields (GraphQL)

| Field | Description |
|-------|-------------|
| `blockedBy` | Issues blocking this issue |
| `blocking` | Issues this issue blocks |
| `subIssues` | Child issues |
| `parent` | Parent issue |
| `trackedIssues` | Issues tracked by this issue |
| `trackedInIssues` | Issues tracking this issue |

### Querying Dependencies

```bash
# Get issues blocking #42
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      issue(number: 42) {
        blockedBy(first: 10) {
          nodes { number title }
        }
        blocking(first: 10) {
          nodes { number title }
        }
      }
    }
  }
'
```

### GTD Mapping

In GTD terms:

- If an action is blocked, set `status/waiting`
- Use GitHub's native blocking to link the blocker issue
- When the blocker is resolved, change to `status/active`

### Example Workflow

```bash
# Check if issue 50 is blocked
gh api graphql -f query='{ repository(owner:"OWNER",name:"REPO") { issue(number:50) { blockedBy(first:5) { nodes { number state } } } } }'

# Update status based on blockers
gtd update 50 --status waiting  # if blocked
gtd update 50 --status active   # when unblocked
```

### Sub-Issues for Projects

GitHub sub-issues can represent GTD project→action relationships:

```bash
# Get sub-issues of a project issue
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      issue(number: 10) {
        subIssues(first: 20) {
          nodes { number title state }
        }
      }
    }
  }
'
```

</dependencies>

<waiting_for>

## Waiting-For Tracking

**The Gap**: GTD's "Waiting For" context tracks *who* you're waiting on, not just that you're waiting.

**Workaround**: Combine `status/waiting` with a text note in the issue body or comment.

### Important: Do NOT Use @mentions

⚠️ **Privacy Warning**: Never use `@username` in waiting-for notes. GitHub @mentions:

- Send notifications to the mentioned person
- May expose sensitive task information to others
- Could leak internal planning details

Instead, use plain text names or initials.

### Convention

When marking something as waiting:

```bash
gtd update 36 --status waiting
gtd comment 36 "Waiting for: Alice (PR review)"
```

Or add to the issue body:

```markdown
Waiting for: Alice to review the PR
```

### Viewing Waiting Items

```bash
# List all waiting items
gtd list --status waiting

# Search for who you're waiting on (plain text)
gh issue list --label status/waiting --json number,title,body | \
  jq -r '.[] | select(.body | contains("Waiting for: Alice"))'
```

### Best Practice

Always document:

1. Who you're waiting for (plain text name, NO @mention)
2. What you're waiting for (specific deliverable)
3. When you started waiting (automatic via comment timestamp)

</waiting_for>

<recurring_tasks>

## Recurring Tasks

**The Gap**: GitHub has no built-in recurring task support.

**Workaround**: Use labels or a dedicated milestone to track recurring tasks.

### Option 1: Label-Based Recurring Tasks

Create a `recurring` label and keep template issues open:

```bash
# Create recurring task label
gh label create "recurring" --color "FBCA04" --description "Recurring task template"

# Create a recurring task template (keep it open)
gtd add "Weekly Review" --context focus --energy low
gh issue edit <number> --add-label recurring

# When it's time, copy it:
gh issue view <template-number> --json title,labels | \
  jq -r '"gtd add \"\(.title)\" --status active"'
```

### Option 2: Recurring Milestone

Create a milestone to group all recurring task templates:

```bash
# Create a "Recurring Tasks" milestone
gh api repos/:owner/:repo/milestones -X POST -f title="Recurring Tasks" \
  -f description="Template issues for recurring tasks - do not close"

# Add templates to the milestone
gh issue edit <number> --milestone "Recurring Tasks"

# List all recurring templates
gh issue list --milestone "Recurring Tasks"
```

### Option 3: Simple Workflow

The simplest approach - just run the GTD review commands which prompt for recurring activities:

```bash
# Weekly - includes recurring review items
gtd weekly

# Daily - surfaces time-sensitive recurring work
gtd daily
```

### Common Recurring Patterns

| Task | Frequency | Approach |
|------|-----------|----------|
| Weekly Review | Weekly | Run `gtd weekly` |
| Inbox Zero | Daily | Run `gtd inbox` |
| Monthly Review | Monthly | Calendar reminder → `gtd add` |
| Quarterly Goals | Quarterly | Run `gtd quarterly` |

### External Reminders

For time-triggered tasks, use your calendar or reminder app to prompt:

```bash
gtd add "Weekly review" --context focus --energy low --status active
```

This keeps GTD simple and avoids over-engineering with GitHub Actions.

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
Waiting for: Alice (PR review)
Defer until: 2026-03-01
```

**Note**: Use GitHub's native GraphQL API for dependencies (`blockedBy`/`blocking`) instead of body conventions.

### Parsing Conventions with jq

```bash
# Find issues due this month
gh issue list --json number,title,body | \
  jq -r '.[] | select(.body | test("Due: 2026-01"))'

# Find issues waiting on someone
gh issue list --label status/waiting --json number,title,body | \
  jq -r '.[] | select(.body | contains("Waiting for:"))'
```

</conventions_summary>

<implemented_commands>

## Implemented CLI Commands

These commands store metadata in a machine-readable HTML comment in the issue body:

```html
<!-- gtd-metadata: {"due":"2026-01-15","defer_until":"2026-03-01","waiting_for":{"person":"Alice","reason":"PR review"},"blocked_by":[42,43]} -->
```

### gtd due - Due Date Management

```bash
gtd due <id> <date>     # Set due date (YYYY-MM-DD)
gtd due <id>            # View due date
gtd due <id> --clear    # Remove due date
```

### gtd defer - Defer Items

```bash
gtd defer <id> <date>           # Defer until date
gtd defer <id> <date> --someday # Defer and set status to someday
```

Items deferred until today or earlier appear in `gtd daily` review.

### gtd waiting - Track Who You're Waiting On

```bash
gtd waiting <id> <person> [reason]  # Mark as waiting
# Example: gtd waiting 42 Alice "PR review"
```

**Important**: Does NOT use @mentions to avoid notifications.

### gtd blocked - Dependency Tracking

```bash
gtd blocked <id> <ids>   # Set blockers (comma-separated)
gtd blocked <id>         # View blockers and their status
gtd blocked <id> --clear # Remove blockers, set status to active
```

### gtd list - Enhanced Filters

```bash
gtd list --due-before 2026-01-31  # Due on or before date
gtd list --overdue                 # Past due date
gtd list --deferred                # Currently deferred
gtd list --not-deferred            # Not deferred
gtd list --blocked                 # Has blockers
gtd list --waiting-on "Alice"      # Waiting on person (partial match)
```

### gtd daily - Enhanced Review

The daily review now includes:

- **Deferred Items Now Active**: Items where defer_until <= today
- **Overdue Items**: Items past due date
- **Blocked Items**: Shows if blockers are resolved

</implemented_commands>

<future_enhancements>

## Potential Future Enhancements

1. ~~**`gtd defer <id> <date>`**: Add defer-until convention~~ ✅ Implemented
2. ~~**`gtd blocked <id> <blocker-ids>`**: Dependency tracking~~ ✅ Implemented
3. ~~**`gtd waiting <id> "person" "reason"`**: Structured waiting-for~~ ✅ Implemented
4. ~~**Due date parsing**: Add `--due-before` filter~~ ✅ Implemented
5. **GitHub Projects integration**: Add `--project-field` options
6. **Sub-issues support**: Integrate with GitHub's native sub-issues

See GitHub issue #5 for discussion and contributions.

</future_enhancements>
