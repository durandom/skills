# Getting Started

Installation, authentication, and project-specific configuration for jira-cli.

## Installation

```bash
which jira  # check if installed
```

If not installed:

```bash
# macOS
brew install ankitpokhrel/jira-cli/jira-cli

# Go install
go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest
```

## Authentication

Run the interactive init (this is the one command that requires interactive input):

```bash
jira init
```

This prompts for:

- **Server:** Your Jira instance URL (e.g., `https://company.atlassian.net`)
- **Login:** Authentication method (API token recommended)
- **Project:** Default project key (optional)

For Atlassian Cloud, generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

Verify with:

```bash
jira me
```

Note: `jira me` returns only the login username. To find your full display name (needed for assignments), inspect any issue assigned to you:

```bash
jira issue view PROJ-123 --raw | jq '.fields.assignee.displayName'
```

## Project Configuration

This skill is project-agnostic. The following settings vary per user and project — persist them somewhere accessible across sessions (e.g., project config, user profile, or dotfiles):

- **Project key** — the default Jira project (e.g., `MYPROJ`)
- **Assignee name** — full display name, not email (find via `jira issue view PROJ-123 --raw | jq '.fields.assignee.displayName'`)
- **Common JQL queries** — frequently used filters
- **Components and labels** — project-specific values
- **Custom fields** — project-specific field keys (e.g., `--custom epic-link=EPIC-XXX`)

When a setting is needed but not found, ask the user and suggest persisting their answer for next time.

### Anti-Patterns

- Don't cache query results — always query live via jira-cli
- Don't hardcode settings in skill files
- Don't store credentials alongside settings — jira-cli handles auth via `~/.config/jira-cli/`
