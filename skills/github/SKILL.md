---
name: github
description: GitHub CLI operations for issues, PRs, reviews, CI, and Copilot workflows. Use when working with pull requests, issues, CI status, code review, GitHub Copilot, triage, or PR shipping.
---

<objective>
Unified interface for GitHub operations using `gh` CLI. Provides patterns for common GitHub workflows including issue triage, PR review, CI monitoring, and Copilot iteration tracking.
</objective>

<quick_start>
For simple queries, use `gh` directly. See [cli-patterns.md](references/cli-patterns.md).

```bash
gh pr list                    # List open PRs
gh issue list                 # List open issues
gh pr view 42                 # View PR #42
gh pr checks 42               # Check CI status
```

</quick_start>

<scripts>
Bundled scripts for data gathering (output JSON, run without loading into context):

- `scripts/triage_gather.sh` - Parallel PR/issue collection
- `scripts/pr_details.sh <number>` - PR info + diff + checks
- `scripts/copilot_activity.sh` - Copilot activity summary
</scripts>

<workflows>
- **Ship PR**: Branch → `/commit` → version bump → PR → Copilot review. See [pr-workflow.md](references/pr-workflow.md)
- **Triage**: See [triage-workflow.md](references/triage-workflow.md)
- **PR Review**: Run `scripts/pr_details.sh`, apply [review-checklist.md](references/review-checklist.md)
- **Copilot Status**: Run `scripts/copilot_activity.sh`
</workflows>

<reference_guides>

- [cli-patterns.md](references/cli-patterns.md) - GH CLI command reference
- [pr-workflow.md](references/pr-workflow.md) - End-to-end PR shipping workflow
- [triage-workflow.md](references/triage-workflow.md) - Full triage workflow
- [review-checklist.md](references/review-checklist.md) - Code review standards
- [copilot-workflow.md](references/copilot-workflow.md) - Copilot iteration patterns
</reference_guides>

<actions>
**Auto-execute (no confirmation):** Post comments, request changes, add labels

**Require confirmation:** merge, approve, close
</actions>

<tips>
- Use `--json` + `--jq` for scripting (more stable than text)
- Include `--limit` for large result sets
- For CI status, check `gh run list --branch` for latest (PR status can be stale)
- Copilot author format varies by repo (check with `gh pr list --state all --json author`)
</tips>

<success_criteria>
GitHub operations are successful when:

- Commands execute without authentication errors
- Data is retrieved in expected format (JSON for scripts, text for quick queries)
- PR/issue state changes are reflected in GitHub UI
- CI status accurately reflects latest workflow runs
</success_criteria>
