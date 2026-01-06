---
name: github
description: GitHub CLI operations for issues, PRs, reviews, CI, and Copilot workflows. Auto-invokes when user asks about PRs, issues, CI status, code review, or GitHub Copilot. Supports triage, PR review, and Copilot iteration patterns.
---

# GitHub Skill

Unified interface for GitHub operations using `gh` CLI.

## Quick Start

For simple queries, use `gh` directly. See [cli-patterns.md](references/cli-patterns.md).

```bash
gh pr list                    # List open PRs
gh issue list                 # List open issues
gh pr view 42                 # View PR #42
gh pr checks 42               # Check CI status
```

## Scripts

Bundled scripts for data gathering (output JSON, run without loading into context):

- `scripts/triage_gather.sh` - Parallel PR/issue collection
- `scripts/pr_details.sh <number>` - PR info + diff + checks
- `scripts/copilot_activity.sh` - Copilot activity summary

## Workflows

- **Triage**: See [triage-workflow.md](references/triage-workflow.md)
- **PR Review**: Run `scripts/pr_details.sh`, apply [review-checklist.md](references/review-checklist.md)
- **Copilot Status**: Run `scripts/copilot_activity.sh`

## References

- [cli-patterns.md](references/cli-patterns.md) - GH CLI command reference
- [triage-workflow.md](references/triage-workflow.md) - Full triage workflow
- [review-checklist.md](references/review-checklist.md) - Code review standards
- [copilot-workflow.md](references/copilot-workflow.md) - Copilot iteration patterns

## Actions

**Auto-execute (no confirmation):** Post comments, request changes, add labels

**Require confirmation:** merge, approve, close

## Tips

- Use `--json` + `--jq` for scripting (more stable than text)
- Include `--limit` for large result sets
- For CI status, check `gh run list --branch` for latest (PR status can be stale)
- Copilot author format varies by repo (check with `gh pr list --state all --json author`)
