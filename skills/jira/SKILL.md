---
name: jira
description: Jira issue management using jira-cli. Search, create, view, comment, and transition issues with JQL queries. Use when working with Jira tickets, Atlassian issues, sprint planning, or issue workflows.
compatibility: Requires jira-cli (https://github.com/ankitpokhrel/jira-cli) installed and authenticated via jira init.
---

<objective>
Unified interface for Jira operations using `jira` CLI. Project-agnostic — store your project-specific settings in CLAUDE.md. See [configuration-guide.md](references/configuration-guide.md).
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

<workflows>

- **Setup**: First-time jira-cli auth and CLAUDE.md configuration — see [setup.md](workflows/setup.md)

</workflows>

<reference_guides>

- [cli-reference.md](references/cli-reference.md) — Command patterns and flags
- [jql-patterns.md](references/jql-patterns.md) — Common JQL queries by use case
- [configuration-guide.md](references/configuration-guide.md) — How to store project settings in CLAUDE.md

</reference_guides>

<tips>

- **Always use `--plain`** for non-interactive output (without it, jira-cli opens a TUI)
- **Always use `--no-input`** for create/edit commands (prevents interactive prompts)
- **Assignee is full display name**, not email — verify with `jira me --raw | jq -r '.displayName'`
- **No ORDER BY in JQL** — jira-cli does not support it, omit the clause
- **Check CLAUDE.md first** for project defaults before asking the user — see [configuration-guide.md](references/configuration-guide.md)
- **Pipe body content** via heredoc or echo — don't rely on the `-b` flag for multi-line text
- **Include `--comments N`** when viewing issues — comments often contain the most relevant context

</tips>

<success_criteria>
Jira operations are successful when:

- Commands execute without authentication errors
- Issues are created with all required fields populated
- JQL queries return expected results
- Project settings are documented in CLAUDE.md for reuse
</success_criteria>
