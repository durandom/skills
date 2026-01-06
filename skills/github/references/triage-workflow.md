# Triage Workflow

Autonomous triage of GitHub PRs and issues. Handles both Copilot PRs (autonomous review) and human PRs (augmented review).

## Design Principles

1. **Autonomous for Copilot**: Full auto-review, post `@copilot` feedback
2. **Augmented for Humans**: User reviews in browser, dictates thoughts, Claude researches & structures
3. **Context-aware**: Quick scan first, deep-dive on priority items only
4. **Session-friendly**: If context fills up, restart with `/triage`

## Phase 1: Gather Data

```bash
scripts/triage_gather.sh
```

## Phase 2: Prioritize

### Pull Requests

| Priority | Category | Action |
|----------|----------|--------|
| P0 | Failing CI on review requests | Deep-dive: analyze failures |
| P0 | Stale Copilot PRs (>3 days) | Deep-dive: review to unblock |
| P1 | Review requested (passing) | Deep-dive: full code review |
| P1 | Copilot PRs ready for review | Deep-dive: full code review |
| Info | Draft PRs, recent merges | Mention only |

### Issues

| Priority | Category | Action |
|----------|----------|--------|
| P1 | Issues blocking PRs | Link to related PRs |
| P2 | `copilot-ready` + unassigned | Offer to enable for Copilot |
| P2 | Unassigned, actionable | List for pickup |
| Info | Assigned/in-progress | Mention status only |

**Only deep-dive on top 2-3 items** to preserve context.

## Phase 3: Deep-Dive

For each priority PR:

```bash
scripts/pr_details.sh <number>
```

Apply [review-checklist.md](review-checklist.md). Check for project-specific coding standards.

### Getting CI Failure Logs

```bash
# Get run ID from branch (not from gh pr checks)
gh run list --branch <headRefName> --limit 3 --json databaseId,conclusion,event

# Get failed logs
gh run view <databaseId> --log-failed

# Filter for errors
gh run view <databaseId> --log-failed 2>&1 | grep -A 5 "Error\|FAIL" | head -50
```

**Note**: PR status can be stale. Always check `gh run list --branch <branch>` for latest.

## Phase 4: Present Report

```markdown
## GitHub Triage Report

### Summary

- X Copilot PRs reviewed (autonomous)
- Y Human PRs awaiting your review
- Z PRs ready to merge
- N issues available for Copilot

---

## Copilot PRs (Autonomous Review)

### PR #<num>: "<title>" [Copilot] <status>

**CI**: Passing/Failing
**Review**: <assessment>

**Issues Found** (if any):
1. <issue with file:line reference>

**Feedback Posted**:
> @copilot please:
> 1. <specific fix>

---

## Human PRs (Awaiting Your Input)

### PR #<num>: "<title>" [by @username] - Needs Review

**CI**: Passing/Failing
**Files**: 5 changed (+120, -45)
**View**: <PR URL>

→ Type `review <num>` to start augmented review

---

## Open Issues

| # | Title | Labels | Assignee | Status |
|---|-------|--------|----------|--------|
| <num> | <title> | <labels> | <assignee or Unassigned> | <status> |

### Issues Ready for Copilot

- #<num>: "<title>" - `copilot-ready`, unassigned
  → Type `copilot <num>` to enable Copilot

### Unassigned Issues (Available for Pickup)

- #<num>: "<title>" - <labels>

---

### Actions Available

**PRs:**
- `merge <num>` - approve and merge PR
- `approve <num>` - approve without merging
- `review <num>` - start augmented review (dictate your feedback)
- `comment <num> <feedback>` - post feedback

**Issues:**
- `copilot <num>` - add `copilot-ready` label to enable Copilot
- `link <pr> <issue>` - link PR to issue (closes on merge)

**General:**
- `close <num>` - close PR/issue
- `done` - finish triage
```

## Phase 5: Execute Actions

**Auto-execute (no confirmation):**

- Post review comments via `gh pr comment`
- Request changes via `gh pr review --request-changes`
- Add labels

**Require confirmation:**

- `merge` - approve and merge
- `approve` - approve without merging
- `close` - close PR/issue

### Merging PRs

**Important**: This repo uses merge commits (not squash). Always use `--merge`.

**Step 1: Approve if needed** (branch protection requires review approval)

```bash
# Check if review is required
gh pr view <num> --json reviewDecision --jq '.reviewDecision'
# Returns: REVIEW_REQUIRED, APPROVED, or CHANGES_REQUESTED

# Approve the PR
gh pr review <num> --approve --body "LGTM"
```

### Step 2: Merge

```bash
# Standard merge (requires approval first)
gh pr merge <num> --merge --delete-branch

# Use admin privileges to bypass branch protection (repo owner only)
gh pr merge <num> --admin --merge --delete-branch
```

**When to use `--admin`:**

- Your own PRs that won't receive external review
- Copilot PRs after autonomous review (no human reviewer)
- Emergency fixes when reviewers are unavailable

**Note**: Only repo admins/owners can use `--admin`. Use judiciously.

### Issue Actions

**Enabling Copilot on an issue:**

GitHub Copilot Coding Agent **self-assigns** when it detects a ready issue. To enable:

```bash
# Add the copilot-ready label (Copilot will pick it up automatically)
gh issue edit <num> --add-label "copilot-ready"

# Verify Copilot picked it up (look for 👀 reaction or Copilot assignee)
gh issue view <num> --json assignees,reactions
```

**Note**: You cannot manually assign `copilot` as a user - Copilot self-assigns after detecting the label.

**Linking issues to PRs:**

```bash
# Add closing reference via comment
gh pr comment <pr-num> --body "Closes #<issue-num>"

# Or edit PR body to include "Fixes #<issue-num>"
```

After each action, ask "Anything else?" When user types `done`, summarize and exit.

## Augmented Review Workflow (Human PRs)

When user types `review <num>`:

### Step 1: Prepare Context

```bash
gh pr view <num> --json title,body,author,files,comments,reviews
gh pr diff <num>
```

Present:

```
## Reviewing PR #<num>: "<title>" by @<author>

**Branch**: <head> → <base>
**Files changed**: <list>
**PR URL**: <url>

Review in your browser, then dictate your thoughts.
I'll research the codebase and structure your feedback.
```

### Step 2: Receive Feedback

User dictates thoughts (concerns, issues, questions, suggestions).

### Step 3: Research & Augment

Based on feedback, research codebase for specific file:line references.

**For architectural feedback**, use Task tool with `subagent_type="Explore"` to find:

- Current implementation of similar features
- Existing patterns to follow
- Specific file paths with line numbers

**For simpler feedback**, use quick Grep/Read searches.

**Always include:**

- Specific `file_path:line_number` references
- Code snippets showing existing patterns
- Table of key files for architectural suggestions

### Step 4: Structure the Review

Transform raw feedback into structured review with:

- Research findings for each concern
- Specific issues with file:line references
- Proposed review comment ready to post

### Step 5: Post Review

On confirmation:

```bash
gh pr review <num> --request-changes --body "<structured review>"
```

## Author-Aware Behavior

| Author | Claude's Role | Your Role |
|--------|---------------|-----------|
| Copilot | Full autonomous review, post feedback | Confirm merge/close |
| Human | Research + structure feedback | Review in browser, dictate |

## Feedback Format for Copilot

**Good:**

```
@copilot please fix:
1. Add test markers to test functions in tests/test_export.py
2. Add return type to `export_data()` in src/export.py:42
```

**Bad:**

```
@copilot fix the code  # Too vague
@copilot this is wrong  # Not actionable
```

## Notes

- If context fills up, complete current PR then present findings
- User can run `/triage` again to continue
- Focus on actionable feedback Copilot can execute
