# Workflow: Jira CLI Setup

First-time setup for jira-cli authentication and project configuration.

<required_reading>

**Read before proceeding:** [configuration-guide.md](configuration-guide.md)

</required_reading>

<process>

## Step 1: Check Installation

```bash
which jira
```

If not installed:

```bash
# macOS
brew install ankitpokhrel/jira-cli/jira-cli

# Go install
go install github.com/ankitpokhrel/jira-cli/cmd/jira@latest
```

## Step 2: Authenticate

Run the interactive init (this is the one command that requires interactive input):

```bash
jira init
```

This prompts for:

- **Server:** Your Jira instance URL (e.g., `https://company.atlassian.net`)
- **Login:** Authentication method (API token recommended)
- **Project:** Default project key (optional, we store this in CLAUDE.md instead)

For Atlassian Cloud, generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

## Step 3: Verify Authentication

```bash
jira me
```

Should display your user profile. If it fails, re-run `jira init`.

Get your display name for assignment (store this — you'll need it):

```bash
jira me --raw | jq -r '.displayName'
```

## Step 4: Gather Project Settings

Use AskUserQuestion to collect:

1. **Primary project key** — What Jira project do you work in most? (e.g., MYPROJ)
2. **Your display name** — Result from `jira me` above
3. **Common queries** — Any JQL you run regularly?
4. **Components/Labels** — Frequently used values?

## Step 5: Generate CLAUDE.md Section

Build a `## Jira Settings` block from the gathered info and add it to CLAUDE.md. See [configuration-guide.md](configuration-guide.md) for the recommended structure and placement.

</process>

<success_criteria>

- `jira me` executes without errors
- User's display name is known
- CLAUDE.md contains a `## Jira Settings` section
- At least project key and assignee name are documented

</success_criteria>
