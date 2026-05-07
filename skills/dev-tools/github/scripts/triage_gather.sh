#!/usr/bin/env bash
# Gather GitHub triage data in parallel
# Outputs JSON with all data needed for triage workflow
set -euo pipefail

# Create temp files for parallel output
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

# Run queries in parallel
gh pr list --json number,title,author,state,isDraft,reviewDecision,statusCheckRollup,labels,updatedAt,headRefName > "$tmp_dir/open_prs.json" &
gh pr list --search "review-requested:@me" --json number,title,author,statusCheckRollup,updatedAt > "$tmp_dir/review_requested.json" &
gh issue list --json number,title,labels,assignees,state,updatedAt > "$tmp_dir/open_issues.json" &
gh issue list --label "copilot-ready" --json number,title,assignees > "$tmp_dir/copilot_ready.json" &
wait

# Filter Copilot PRs from open_prs (author login contains "copilot")
jq '[.[] | select(.author.login | test("copilot"; "i"))]' "$tmp_dir/open_prs.json" > "$tmp_dir/copilot_prs.json"

# Combine into single JSON object
jq -n \
  --slurpfile open_prs "$tmp_dir/open_prs.json" \
  --slurpfile copilot_prs "$tmp_dir/copilot_prs.json" \
  --slurpfile review_requested "$tmp_dir/review_requested.json" \
  --slurpfile open_issues "$tmp_dir/open_issues.json" \
  --slurpfile copilot_ready "$tmp_dir/copilot_ready.json" \
  '{
    open_prs: $open_prs[0],
    copilot_prs: $copilot_prs[0],
    review_requested: $review_requested[0],
    open_issues: $open_issues[0],
    copilot_ready_issues: $copilot_ready[0]
  }'
