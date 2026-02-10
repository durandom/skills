# Jira CLI Setup

First-time setup for jira-cli installation and authentication.

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
- **Project:** Default project key (optional)

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

</process>

<success_criteria>

- `jira me` executes without errors
- User's display name is known

</success_criteria>
