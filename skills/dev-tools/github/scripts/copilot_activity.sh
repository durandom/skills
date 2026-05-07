#!/usr/bin/env bash
# Get GitHub Copilot activity summary
# Outputs JSON with Copilot PRs, assigned issues, and recent merges
set -euo pipefail

# Create temp files for parallel output
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

# Run queries in parallel
gh pr list --state open --json number,title,author,headRefName,createdAt,reviews,statusCheckRollup > "$tmp_dir/open_prs.json" &
gh pr list --state merged --limit 20 --json number,title,author,mergedAt > "$tmp_dir/merged_prs.json" &
gh issue list --state open --json number,title,createdAt,labels,assignees > "$tmp_dir/all_issues.json" &
gh issue list --label "copilot-ready" --state open --json number,title,assignees > "$tmp_dir/copilot_ready.json" &
wait

# Filter Copilot PRs (author login contains "copilot")
jq '[.[] | select(.author.login | test("copilot"; "i"))]' "$tmp_dir/open_prs.json" > "$tmp_dir/copilot_open.json"
jq '[.[] | select(.author.login | test("copilot"; "i"))]' "$tmp_dir/merged_prs.json" > "$tmp_dir/copilot_merged.json"

# Filter issues assigned to Copilot
jq '[.[] | select(.assignees[].login | test("copilot"; "i"))]' "$tmp_dir/all_issues.json" > "$tmp_dir/assigned_issues.json"

# Combine into single JSON object
jq -n \
  --slurpfile open_prs "$tmp_dir/copilot_open.json" \
  --slurpfile merged_prs "$tmp_dir/copilot_merged.json" \
  --slurpfile assigned_issues "$tmp_dir/assigned_issues.json" \
  --slurpfile copilot_ready "$tmp_dir/copilot_ready.json" \
  '{
    open_prs: $open_prs[0],
    recently_merged: $merged_prs[0],
    assigned_issues: $assigned_issues[0],
    copilot_ready_unassigned: [$copilot_ready[0][] | select(.assignees | length == 0)]
  }'
