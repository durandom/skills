#!/usr/bin/env bash
# Get comprehensive PR details for review
# Usage: pr_details.sh <pr-number>
set -euo pipefail

PR_NUM="${1:?Usage: pr_details.sh <pr-number>}"

# Create temp files for parallel output
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

# Fetch PR metadata and checks in parallel
gh pr view "$PR_NUM" --json title,body,state,author,headRefName,baseRefName,files,reviews,comments,labels > "$tmp_dir/pr.json" &
gh pr checks "$PR_NUM" --json name,state,conclusion 2>/dev/null > "$tmp_dir/checks.json" || echo '[]' > "$tmp_dir/checks.json" &
wait

# Get branch name for run lookup
BRANCH=$(jq -r '.headRefName' "$tmp_dir/pr.json")

# Get latest CI run info
gh run list --branch "$BRANCH" --limit 3 --json databaseId,conclusion,status,event > "$tmp_dir/runs.json" 2>/dev/null || echo '[]' > "$tmp_dir/runs.json"

# Combine metadata
jq -n \
  --slurpfile pr "$tmp_dir/pr.json" \
  --slurpfile checks "$tmp_dir/checks.json" \
  --slurpfile runs "$tmp_dir/runs.json" \
  '{
    pr: $pr[0],
    checks: $checks[0],
    runs: $runs[0]
  }'

# Output diff separately (not JSON, marked for parsing)
echo ""
echo "---DIFF-START---"
gh pr diff "$PR_NUM"
echo "---DIFF-END---"
