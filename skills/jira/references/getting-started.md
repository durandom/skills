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

Get your display name for assignment:

```bash
jira me --raw | jq -r '.displayName'
```

## Project Configuration

This skill is project-agnostic. Store project-specific settings in CLAUDE.md where they are version-controlled and team-shareable.

### Recommended CLAUDE.md Structure

```markdown
## Jira Settings

**Project Key:** MYPROJ
**Assignee Name:** "Jane Smith"

**Common Queries:**
- My work: `assignee = currentUser() AND status != Done`
- Sprint: `project = MYPROJ AND sprint in openSprints()`
- Triage: `type = Bug AND status = "To Do" AND priority is EMPTY`

**Components:** Backend, API, Frontend
**Labels:** bug-fix, feature, tech-debt

**Custom Fields:**
- Epic link: `--custom epic-link=EPIC-XXX`
- Story points: `--custom customfield_10016=N`
```

### Settings Resolution Order

1. **Project CLAUDE.md** `./CLAUDE.md` — highest priority
2. **User CLAUDE.md** `~/.claude/CLAUDE.md` — personal defaults
3. **Ask interactively** — use AskUserQuestion as last resort
4. **Suggest saving** — after asking, propose adding to CLAUDE.md

### Anti-Patterns

- Don't create separate config files (`.jira-config.json`, `.jira.yml`)
- Don't cache query results — always query live via jira-cli
- Don't hardcode settings in skill files
- Don't store credentials in CLAUDE.md — jira-cli handles auth via `~/.config/jira-cli/`
