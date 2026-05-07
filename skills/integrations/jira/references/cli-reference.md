# Jira CLI Reference

Quick reference for `jira` CLI commands. All commands use non-interactive flags for agent compatibility.

## Essential Flags

```bash
--plain       # Non-interactive text output (REQUIRED for agents)
--no-input    # Skip interactive prompts (REQUIRED for create/edit)
--raw         # JSON output for parsing (jira issue view only, NOT jira me)
--comments N  # Include N recent comments in view
```

## Issues

```bash
# List
jira issue list --plain
jira issue list --jql 'assignee = currentUser() AND status not in (Done)' --plain
jira issue list -s "In Progress" --plain

# View
jira issue view PROJ-123 --plain
jira issue view PROJ-123 --comments 10 --plain
jira issue view PROJ-123 --raw  # JSON for parsing

# Create (always pipe body or use heredoc)
jira issue create -pPROJ -tTask -s"Summary" --no-input <<'EOF'
Description here.
Multi-line supported.
EOF

# Create with echo pipe
echo "Description" | jira issue create -pPROJ -tTask -s"Summary" --no-input

# Create with short body flag
jira issue create -pPROJ -tBug -s"Summary" -b"Short description" --no-input

# Edit
jira issue edit PROJ-123 -s"New summary" --no-input

# Assign (MUST use full display name, not email)
jira issue assign PROJ-123 "Jane Smith"

# Unassign
jira issue assign PROJ-123 x

# Comment
echo "Comment text" | jira issue comment add PROJ-123 --no-input

# Transition
jira issue move PROJ-123 "In Progress" --no-input
jira issue move PROJ-123 "Done" --no-input

# Link
jira issue link PROJ-1 PROJ-2 "relates to"
jira issue link PROJ-1 PROJ-2 "blocks"
jira issue link PROJ-1 PROJ-2 "duplicates"
```

## Create Flags

```bash
-p, --project     # Project key (e.g., MYPROJ)
-t, --type        # Issue type: Bug, Task, Story, Epic
-s, --summary     # One-line summary
-b, --body        # Description (prefer heredoc/pipe for multi-line)
-y, --priority    # Critical, High, Medium, Low
-a, --assignee    # Full display name
-l, --label       # Label (repeatable: -lbackend -lurgent)
-C, --component   # Component (repeatable)
-R, --resolution  # Resolution: Fixed, Won't Fix, Duplicate
```

## Custom Fields

```bash
# Epic link
--custom epic-link=EPIC-123

# Parent link (subtask)
--custom parent-link=PARENT-456

# Discover custom field keys
jira issue view PROJ-123 --raw | jq '.fields | keys'

# Arbitrary custom field
--custom customfield_10016=5
```

## Assignee Format

Assignee MUST be the full display name as shown in Jira, not the email address.

```bash
# Find your display name (jira me only returns login, use an assigned issue)
jira issue view PROJ-123 --raw | jq -r '.fields.assignee.displayName'

# Correct
jira issue assign PROJ-123 "Jane Smith"

# Wrong - will fail
jira issue assign PROJ-123 "jane@company.com"
```

## Sprints and Epics

```bash
jira sprint list --plain
jira sprint list --state active --plain
jira epic list --plain
jira epic list -pPROJ --plain
```

## Anti-Patterns

```bash
# != can break in double-quoted JQL (interactive shells may expand ! as history)
jira issue list --jql "status != Done"                        # May fail in interactive shells
jira issue list --jql 'status != Done'                        # OK: single quotes prevent expansion
jira issue list --jql 'status not in (Done)'                  # BEST: avoids the issue entirely

# No ORDER BY in JQL (jira-cli limitation)
jira issue list --jql "status = Open ORDER BY updated"      # FAILS
jira issue list --jql "status = Open"                        # OK

# Always use --plain for agents
jira issue list                                               # Opens interactive TUI
jira issue list --plain                                       # Returns parseable text

# Always use --no-input for create/edit
jira issue create -pPROJ -tTask -s"Summary"                  # Prompts for body
echo "Body" | jira issue create -pPROJ -tTask -s"Summary" --no-input  # Non-interactive
```
