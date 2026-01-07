<overview>
GitHub Issues provides a solid foundation for GTD. This document explains how GTD concepts map to GitHub features and the CLI commands that bridge any gaps.

**TL;DR**: Most GTD concepts work natively with labels and milestones. The GTD CLI adds commands for due dates, deferring, waiting-for tracking, and dependencies.
</overview>

<concept_mapping>

## GTD Concepts → GitHub Mapping

| GTD Concept | GitHub Feature | CLI Command |
|-------------|----------------|-------------|
| Actions/Tasks | Issues | `gtd add`, `gtd done` |
| Projects | Milestones | `gtd add --project` |
| Contexts | Labels (context/*) | `gtd update --context` |
| Status | Labels (status/*) | `gtd update --status` |
| Energy | Labels (energy/*) | `gtd update --energy` |
| Horizons | Labels (horizon/*) | `gtd update --horizon` |
| Due Dates | Metadata in body | `gtd due` |
| Defer/Tickler | Metadata in body | `gtd defer` |
| Dependencies | Metadata in body | `gtd blocked` |
| Waiting-For | Metadata in body | `gtd waiting` |
| Recurring Tasks | Manual | See [Recurring Tasks](#recurring-tasks) |
| Someday/Maybe | status/someday label | `gtd update --status someday` |

</concept_mapping>

<metadata_storage>

## How Metadata Works

The CLI stores GTD metadata as an invisible HTML comment in the issue body:

```html
<!-- gtd-metadata: {"due":"2026-01-15","defer_until":"2026-03-01","waiting_for":{"person":"Alice","reason":"PR review"},"blocked_by":[42,43]} -->
```

This format:

- Is invisible in rendered GitHub markdown
- Machine-parseable JSON
- Won't conflict with existing body content
- Survives issue edits in the GitHub UI

</metadata_storage>

<cli_commands>

## CLI Commands Reference

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

**Important**: Does NOT use @mentions to avoid notifications. See [Privacy Warning](#privacy-warning-mentions).

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

The daily review includes:

- **Deferred Items Now Active**: Items where defer_until <= today
- **Overdue Items**: Items past due date
- **Blocked Items**: Shows if blockers are resolved

</cli_commands>

<privacy_warning>

## Privacy Warning: @mentions

**Never use `@username` in waiting-for notes.** GitHub @mentions:

- Send notifications to the mentioned person
- May expose sensitive task information to others
- Could leak internal planning details

The `gtd waiting` command stores plain text names, not @mentions. Always use plain text names or initials when tracking who you're waiting on.

</privacy_warning>

<recurring_tasks>

## Recurring Tasks

**The Gap**: GitHub has no built-in recurring task support. This requires manual handling.

### Simple Workflow (Recommended)

Use GTD review commands which prompt for recurring activities:

```bash
gtd weekly   # Weekly review - includes recurring review items
gtd daily    # Daily - surfaces time-sensitive recurring work
```

### Template-Based Approach

Create a `recurring` label and keep template issues open:

```bash
# Create recurring task label
gh label create "recurring" --color "FBCA04" --description "Recurring task template"

# Create a recurring task template (keep it open)
gtd add "Weekly Review" --context focus --energy low
gh issue edit <number> --add-label recurring

# List all recurring templates
gh issue list --label recurring
```

### External Reminders

For time-triggered tasks, use your calendar or reminder app to prompt:

```bash
gtd add "Weekly review" --context focus --energy low --status active
```

This keeps GTD simple and avoids over-engineering.

</recurring_tasks>

<github_native_features>

## GitHub Native Features

### Issue Dependencies (GraphQL)

GitHub has native dependency fields accessible via GraphQL:

| Field | Description |
|-------|-------------|
| `blockedBy` | Issues blocking this issue |
| `blocking` | Issues this issue blocks |
| `subIssues` | Child issues |
| `parent` | Parent issue |

The `gtd blocked` command uses metadata for simplicity, but you can query native dependencies:

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      issue(number: 42) {
        blockedBy(first: 10) { nodes { number title state } }
        blocking(first: 10) { nodes { number title state } }
      }
    }
  }
'
```

### GitHub Projects (Advanced)

GitHub Projects offers additional custom fields (dates, numbers, single-select). Consider Projects integration if you need:

- Due date filtering in GitHub UI
- Kanban board visualization
- Sprint/iteration planning

```bash
gh project list                                    # List projects
gh project item-list <number> --owner <owner>      # View items
```

**Recommendation**: Start with labels and CLI commands. Add Projects integration only if you need the visual board or advanced filtering in the GitHub UI.

</github_native_features>

<future_enhancements>

## Potential Future Enhancements

1. **GitHub Projects integration**: Add `--project-field` options for custom date fields
2. **Sub-issues support**: Integrate with GitHub's native sub-issues for project→action relationships
3. **Recurring task automation**: Template duplication via CLI

See GitHub issues for discussion and contributions.

</future_enhancements>
