# JQL Patterns

Common JQL queries for use with `jira issue list --jql "..." --plain`.

**Limitation:** jira-cli does NOT support `ORDER BY` clauses. Omit them.

## Personal Work

```sql
-- My open issues
assignee = currentUser() AND status != Done

-- My recent updates
assignee = currentUser() AND updated >= -7d

-- My high priority
assignee = currentUser() AND priority in (Critical, High)

-- Issues I'm watching
watcher = currentUser()
```

## Team Work

```sql
-- Current sprint
project = PROJ AND sprint in openSprints()

-- Team members' active work
assignee in ("Jane Smith", "John Doe") AND status = "In Progress"

-- Unassigned work
project = PROJ AND assignee is EMPTY AND status = "To Do"
```

## Bug Tracking

```sql
-- Bugs needing triage (no priority set)
type = Bug AND status = "To Do" AND priority is EMPTY

-- Critical open bugs
type = Bug AND priority = Critical AND status != Done

-- Bugs by component
type = Bug AND component = Backend AND status != Done
```

## Time Filters

```sql
-- Created in last 7 days
created >= -7d

-- Updated in last hour
updated >= -1h

-- Created this week
created >= startOfWeek()

-- Due this month
due <= endOfMonth()

-- Overdue
due < now() AND status != Done
```

## Labels and Components

```sql
-- By label
labels = "tech-debt"

-- By component
component = API

-- No component set
component is EMPTY

-- Multiple labels
labels in (backend, urgent)
```

## Combining Filters

```sql
-- Complex example
project = PROJ
  AND type = Bug
  AND status IN ("To Do", "In Progress")
  AND priority in (High, Critical)
  AND created >= -30d

-- Text search
summary ~ "login" OR description ~ "login"

-- Exclude specific status
status NOT IN (Done, Closed, Cancelled)
```

## Limitations

```sql
-- ORDER BY not supported by jira-cli
status = "In Progress" ORDER BY updated    -- FAILS, remove ORDER BY

-- Use IN for multiple values instead of OR chains
status IN ("To Do", "In Progress")         -- preferred
status = "To Do" OR status = "In Progress" -- works but verbose
```
