# GitHub CLI Patterns

Quick reference for `gh` CLI commands. Use these patterns directly.

## Issues

```bash
# List
gh issue list [--state open] [--label bug] [--assignee @me]
gh issue list --search "keyword in:title"

# View
gh issue view <number> [--json title,body,state,labels]

# Create
gh issue create --title "..." --body "..." --label "bug"

# Edit
gh issue edit <number> --add-label "urgent"
gh issue edit <number> --add-assignee "@me"
gh issue edit <number> --remove-label "needs-review"

# Close
gh issue close <number> [--reason completed]
gh issue reopen <number>
```

## Pull Requests

```bash
# List
gh pr list [--state open] [--author <author>]
gh pr list --search "export in:title"
gh pr list --label "needs-review"

# View
gh pr view <number>
gh pr view <number> --json title,body,state,files,reviews,statusCheckRollup
gh pr diff <number>

# Create
git push -u origin <branch>
gh pr create --title "..." --body "..."

# Review
gh pr review <number> --approve
gh pr review <number> --request-changes --body "Please fix..."
gh pr review <number> --comment --body "Looks good..."

# Merge (this repo uses merge commits, not squash)
gh pr merge <number> --merge [--delete-branch]

# Other
gh pr checkout <number>
gh pr close <number>
gh pr comment <number> --body "..."
```

## CI/Checks

```bash
# View PR checks
gh pr checks <number>

# Get run details (use branch name, not PR number)
gh run list --branch <branch> --limit 3 --json databaseId,conclusion,status

# View failed logs
gh run view <run-id> --log-failed

# Filter errors
gh run view <run-id> --log-failed 2>&1 | grep -A 5 "Error\|FAIL" | head -50
```

## Comments

```bash
# PR comment
gh pr comment <number> --body "..."

# Get review comments (inline)
gh api repos/{owner}/{repo}/pulls/<number>/comments \
  --jq '.[] | {id, author: .user.login, body, path, line}'

# Get issue comments
gh api repos/{owner}/{repo}/issues/<number>/comments \
  --jq '.[] | {id, author: .user.login, body}'

# Reply to comment
gh api repos/{owner}/{repo}/pulls/comments/<comment-id>/replies \
  -f body="Fixed in abc1234"
```

## JSON Filtering

```bash
# Custom jq filtering
gh pr list --json number,title,author --jq '.[] | "\(.number): \(.title)"'

# Filter by field
gh issue list --json number,title,assignees --limit 100 \
  --jq '[.[] | select(.assignees[].login == "Copilot")]'
```

### jq Escaping Gotcha

**Avoid `!=` in jq expressions** - bash interprets `!` as history expansion even in double quotes.

```bash
# ❌ BROKEN - bash expands != as history reference
gh pr view 1 --jq '.reviews | map(select(.state != "COMMENTED"))'

# ✅ WORKS - use "not" pattern instead
gh pr view 1 --jq '.reviews | map(select(.state == "COMMENTED" | not))'

# ✅ WORKS - use set +H to disable history expansion
set +H && gh pr view 1 --jq '.reviews | map(select(.state != "COMMENTED"))'
```

## Copilot-Specific

```bash
# List Copilot PRs (author varies by repo, check with gh pr list --state all --json author)
gh pr list --author "app/copilot-swe-agent"  # or "app/github-copilot"

# Trigger Copilot iteration
gh pr comment <number> --body "@copilot please fix the type error"

# Assign issue to Copilot (CLI doesn't work, use web UI)
# https://github.com/<owner>/<repo>/issues/<number>
```
