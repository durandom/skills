# Jira Configuration Guide

How to store project-specific Jira settings so this skill can use them across sessions.

## Philosophy

This skill is intentionally project-agnostic. Instead of hardcoding projects, teams, or queries, store your settings in CLAUDE.md where they are version-controlled and team-shareable.

## Recommended CLAUDE.md Structure

Add to your project's `CLAUDE.md`:

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

## Settings Resolution Order

When a workflow needs a setting (e.g., project key):

1. **Project CLAUDE.md** `./CLAUDE.md` — highest priority
2. **User CLAUDE.md** `~/.claude/CLAUDE.md` — personal defaults
3. **Ask interactively** — use AskUserQuestion as last resort
4. **Suggest saving** — after asking, propose adding to CLAUDE.md

## Pattern for Workflows

Every workflow should follow this pattern for settings:

1. Check CLAUDE.md for the needed value
2. Use it if found
3. Ask the user if not found
4. After a successful operation, suggest saving any new values

Example: "I used project key MYPROJ for this issue. Want me to add that as your default in CLAUDE.md?"

## Where to Store Settings

| Scope | Location | Use Case |
|-------|----------|----------|
| Project-specific | `./CLAUDE.md` | Team shares project key, components, queries |
| Personal defaults | `~/.claude/CLAUDE.md` | Your assignee name, cross-project preferences |

## Anti-Patterns

- Don't create separate config files (`.jira-config.json`, `.jira.yml`)
- Don't cache query results — always query live via jira-cli
- Don't hardcode settings in skill files
- Don't store credentials in CLAUDE.md — jira-cli handles auth via `~/.config/jira-cli/`
