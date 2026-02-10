---
name: jira
description: Jira issue management using jira-cli. Search, create, view, comment, and transition issues with JQL queries. Use when working with Jira tickets, Atlassian issues, sprint planning, or issue workflows.
compatibility: Requires jira-cli (https://github.com/ankitpokhrel/jira-cli) installed and authenticated via jira init.
---

<objective>
Manage Jira issues using `jira` CLI — search, create, view, comment, and transition issues without leaving the terminal.
</objective>

<quick_start>
For simple queries, use `jira` directly. See [cli-reference.md](references/cli-reference.md).

```bash
jira issue list --plain                                        # List issues
jira issue view PROJ-123 --comments 5 --plain                  # View with comments
jira issue create -pPROJ -tTask -s"Summary" --no-input <<< "Description"  # Create
jira issue move PROJ-123 "In Progress" --no-input              # Transition
echo "Comment" | jira issue comment add PROJ-123 --no-input    # Comment
jira issue assign PROJ-123 "Jane Smith"                        # Assign (full name!)
```

</quick_start>

<reference_guides>

- [getting-started.md](references/getting-started.md) — Installation, auth, and project configuration
- [cli-reference.md](references/cli-reference.md) — Command patterns and flags
- [jql-patterns.md](references/jql-patterns.md) — Common JQL queries by use case

</reference_guides>

<tips>

- **Always use `--plain`** for non-interactive output (without it, jira-cli opens a TUI)
- **Always use `--no-input`** for create/edit commands (prevents interactive prompts)
- **Assignee is full display name**, not email — `jira me` returns login only; find display name from any assigned issue via `jira issue view PROJ-123 --raw | jq -r '.fields.assignee.displayName'`
- **`!=` in JQL can break** — interactive shells may interpret `!` in double quotes as history expansion; use single quotes or prefer `not in (Done)`
- **No ORDER BY in JQL** — jira-cli does not support it, omit the clause
- **Check for stored project defaults** before asking the user — see [getting-started.md](references/getting-started.md)
- **Pipe body content** via heredoc or echo — don't rely on the `-b` flag for multi-line text
- **Include `--comments N`** when viewing issues — comments often contain the most relevant context

</tips>

<success_criteria>
Jira operations are successful when:

- Commands execute without authentication errors
- Issues are created with all required fields populated
- JQL queries return expected results
- Project settings are persisted for reuse across sessions
</success_criteria>
