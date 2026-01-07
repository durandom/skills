# GitHub Copilot Workflow

Patterns for working with GitHub Copilot Coding Agent.

## Workflow States

```
Issue Created
    │
    ▼
Assigned to Copilot ──▶ Copilot Working (👀 reaction)
    │
    ▼
PR Created (Draft) ──▶ CI Running
    │
    ├─▶ CI Passing ──▶ Needs Review
    │                      │
    │                      ├─▶ Approved ──▶ Ready to Merge
    │                      │
    │                      └─▶ Changes Requested ──▶ Copilot iterates
    │
    └─▶ CI Failing ──▶ Needs Investigation
                           │
                           └─▶ @copilot feedback ──▶ Copilot fixes
```

## Posting Feedback

Use specific, actionable feedback:

**Good:**

```
@copilot please fix:
1. Add test markers to test functions in tests/test_export.py
2. Add return type annotation to `export_data()` in src/export.py:42
3. Fix the linting error on line 15
```

**Bad (avoid):**

```
@copilot fix the code  # Too vague
@copilot this is wrong  # Not actionable
@copilot add tests, fix types, update docs  # Too many things at once
```

## Augmented Review (Human PRs)

For human-authored PRs, use dictation workflow:

1. Review PR in browser
2. Dictate your thoughts to Claude
3. Claude researches codebase for specific file:line references
4. Claude structures feedback into actionable review
5. Post via `gh pr review --request-changes`

## Author Detection

```bash
# Find Copilot author format for this repo
gh pr list --state all --limit 20 --json author --jq '[.[].author.login] | unique'

# Copilot PRs (author varies: "app/copilot-swe-agent" or "app/github-copilot")
gh pr list --author "app/copilot-swe-agent"

# Human PRs needing review
gh pr list --search "review-requested:@me"
```

| Author | Claude's Role | Your Role |
|--------|---------------|-----------|
| Copilot | Full autonomous review, posts feedback | Confirm merge/close |
| Human | Research assistant, structures feedback | Review in browser, dictate thoughts |

## Assigning Issues to Copilot

As of January 2026, CLI assignment doesn't work for Copilot. Use web UI:

1. Go to issue URL
2. Click "Assignees" in right sidebar
3. Select "Copilot"

Copilot will react with 👀 when it starts working.

## Iterating on Copilot PRs

```bash
# Post feedback
gh pr comment <number> --body "@copilot please add type hints to process()"

# Check if Copilot updated
gh pr view <number> --json commits --jq '.commits[-1]'

# Re-check CI
gh pr checks <number>
```

## Browser Fallbacks

Some operations require browser:

- **Assign issue to Copilot**: `https://github.com/<owner>/<repo>/issues/<num>`
- **Re-request review**: Use PR page
- **Complex merge conflicts**: Resolve in browser or locally

## CI Status Notes

PR status can be stale. Always verify with:

```bash
# Get latest run for branch
gh run list --branch <branch> --limit 1 --json conclusion,status

# A PR may show "failing" even when latest commit passed
```
