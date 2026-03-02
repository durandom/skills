#!/usr/bin/env bash
# migrate-github-to-beads.sh — Migrate GitHub Issues into the GTD Beads backend
#
# USAGE
#   ./migrate-github-to-beads.sh <owner/repo> [--logfile <path>] [--dry-run]
#
# REQUIREMENTS
#   - gtd (skills/gtd/scripts/gtd) on PATH, configured for the beads backend
#   - bd  (beads CLI) on PATH
#   - gh  (GitHub CLI) on PATH, authenticated for the target repo
#   - python3
#
# IDEMPOTENCY
#   Each migrated item receives a "migrated:gh-<NUM>" label.
#   Re-running the script is safe — already-migrated issues are skipped.
#
# WHAT IS MIGRATED
#   - GitHub milestones  → GTD projects  (description + due date from GitHub)
#   - GitHub issues      → GTD items     (title, body, GTD labels, project, state)
#   - Issue comments     → GTD comments  (in order)
#   - Closed issues      → marked done in GTD
#   - A provenance comment is added to every item: "Migrated from GitHub issue #N"
#
# GTD LABEL MAPPING (GitHub label → GTD field)
#   context/<value>  → --context <value>
#   energy/<value>   → --energy  <value>
#   status/<value>   → --status  <value>
#   horizon/<value>  → --horizon <value>
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <owner/repo> [--logfile <path>] [--dry-run]" >&2
  exit 1
fi

REPO="$1"; shift
LOGFILE="migrate-gtd.log"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --logfile) LOGFILE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

GTD="gtd"
if ! command -v "$GTD" &>/dev/null; then
  echo "ERROR: 'gtd' not found on PATH. Add skills/gtd/scripts/ to PATH first." >&2
  exit 1
fi

echo "=== GTD Migration: GitHub ($REPO) → Beads ===" | tee "$LOGFILE"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOGFILE"
[[ "$DRY_RUN" == true ]] && echo "DRY-RUN: no writes will be made" | tee -a "$LOGFILE"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
json_field() {
  # json_field <field> <<< "$json_string"
  local field="$1"
  python3 -c "import sys,json; print(json.load(sys.stdin).get('${field}') or '')"
}

json_label_field() {
  # Extract a single GTD label category from labels array
  # json_label_field <category> <<< "$json_string"
  local cat="$1"
  python3 -c "
import sys,json
labels=[l['name'] for l in json.load(sys.stdin).get('labels',[])]
vals=[l.split('/')[1] for l in labels if l.startswith('${cat}/')]
print(vals[0] if vals else '')
"
}

is_migrated() {
  local num="$1"
  local result
  result=$(bd list --json --label "migrated:gh-${num}" --limit 1 2>/dev/null || echo "[]")
  [[ "$result" != "[]" && -n "$result" ]]
}

run_or_dry() {
  if [[ "$DRY_RUN" == true ]]; then
    echo "    [dry-run] $*" | tee -a "$LOGFILE"
  else
    "$@" 2>&1 | tee -a "$LOGFILE"
  fi
}

# ---------------------------------------------------------------------------
# Step 1: Create projects from GitHub milestones
# ---------------------------------------------------------------------------
echo "" | tee -a "$LOGFILE"
echo "--- Step 1: Creating projects from GitHub milestones ---" | tee -a "$LOGFILE"

gh api "repos/${REPO}/milestones?state=all&per_page=100" | python3 -c "
import sys, json
for m in json.load(sys.stdin):
    due = (m.get('due_on') or '')[:10]  # ISO date or empty
    desc = m.get('description') or ''
    print(m['title'] + '\t' + desc + '\t' + due)
" | while IFS=$'\t' read -r title desc due; do
  echo "  Creating project: $title" | tee -a "$LOGFILE"
  args=("project" "create" "$title")
  [[ -n "$desc" ]] && args+=("--desc" "$desc")
  [[ -n "$due"  ]] && args+=("--due"  "$due")
  run_or_dry "$GTD" "${args[@]}"
done

# ---------------------------------------------------------------------------
# Step 2: Migrate issues
# ---------------------------------------------------------------------------
echo "" | tee -a "$LOGFILE"
echo "--- Step 2: Migrating issues ---" | tee -a "$LOGFILE"

ISSUES=$(gh issue list --repo "$REPO" --state all --limit 500 --json number \
  --jq '.[].number' | sort -n)

MIGRATED=0
SKIPPED=0
FAILED=0

for NUM in $ISSUES; do
  echo "" | tee -a "$LOGFILE"
  echo "  === Issue #$NUM ===" | tee -a "$LOGFILE"

  if is_migrated "$NUM"; then
    echo "  SKIP: already migrated (migrated:gh-$NUM)" | tee -a "$LOGFILE"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  DATA=$(gh issue view "$NUM" --repo "$REPO" \
    --json number,title,body,state,labels,createdAt,closedAt,milestone,comments)

  TITLE=$(echo "$DATA"     | json_field title)
  STATE=$(echo "$DATA"     | json_field state)
  BODY=$(echo "$DATA"      | json_field body)
  MILESTONE=$(echo "$DATA" | python3 -c "
import sys,json; m=json.load(sys.stdin).get('milestone'); print(m['title'] if m else '')
")
  CONTEXT=$(echo "$DATA"   | json_label_field context)
  ENERGY=$(echo "$DATA"    | json_label_field energy)
  GTD_STATUS=$(echo "$DATA"| json_label_field status)
  HORIZON=$(echo "$DATA"   | json_label_field horizon)

  ADD_ARGS=("add" "$TITLE")
  [[ -n "$CONTEXT"    ]] && ADD_ARGS+=("--context" "$CONTEXT")
  [[ -n "$ENERGY"     ]] && ADD_ARGS+=("--energy"  "$ENERGY")
  [[ -n "$GTD_STATUS" ]] && ADD_ARGS+=("--status"  "$GTD_STATUS")
  [[ -n "$HORIZON"    ]] && ADD_ARGS+=("--horizon" "$HORIZON")
  [[ -n "$MILESTONE"  ]] && ADD_ARGS+=("--project" "$MILESTONE")
  [[ -n "$BODY"       ]] && ADD_ARGS+=("--body"    "$BODY")

  if [[ "$DRY_RUN" == true ]]; then
    echo "    [dry-run] $GTD ${ADD_ARGS[*]}" | tee -a "$LOGFILE"
    MIGRATED=$((MIGRATED + 1))
    continue
  fi

  CREATE_OUTPUT=$("$GTD" "${ADD_ARGS[@]}" 2>&1)
  echo "$CREATE_OUTPUT" | tee -a "$LOGFILE"
  BEAD_ID=$(echo "$CREATE_OUTPUT" | grep -oE '#[A-Z]+-[a-z0-9.]+' | head -1 | tr -d '#')

  if [[ -z "$BEAD_ID" ]]; then
    echo "  ERROR: failed to extract bead ID for issue #$NUM" | tee -a "$LOGFILE"
    FAILED=$((FAILED + 1))
    continue
  fi

  # Idempotency label
  bd update "$BEAD_ID" --add-label "migrated:gh-${NUM}" --quiet 2>&1 | tee -a "$LOGFILE"

  # Migrate comments (in order)
  COMMENT_COUNT=$(echo "$DATA" | python3 -c "
import sys,json; print(len(json.load(sys.stdin).get('comments',[])))
")
  for i in $(seq 0 $((COMMENT_COUNT - 1))); do
    COMMENT_BODY=$(echo "$DATA" | python3 -c "
import sys,json; print(json.load(sys.stdin)['comments'][$i]['body'])
")
    "$GTD" comment "$BEAD_ID" "$COMMENT_BODY" 2>&1 | tee -a "$LOGFILE"
  done

  # Provenance
  "$GTD" comment "$BEAD_ID" \
    "Migrated from GitHub issue #${NUM}: https://github.com/${REPO}/issues/${NUM}" \
    2>&1 | tee -a "$LOGFILE"

  # Close if original was closed
  [[ "$STATE" == "CLOSED" ]] && "$GTD" done "$BEAD_ID" 2>&1 | tee -a "$LOGFILE"

  echo "  ✓ #${NUM} → $BEAD_ID (state=$STATE, project=${MILESTONE:-none})" \
    | tee -a "$LOGFILE"
  MIGRATED=$((MIGRATED + 1))
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "" | tee -a "$LOGFILE"
echo "=== Migration complete ===" | tee -a "$LOGFILE"
echo "  Migrated: $MIGRATED" | tee -a "$LOGFILE"
echo "  Skipped:  $SKIPPED  (already migrated)" | tee -a "$LOGFILE"
echo "  Failed:   $FAILED" | tee -a "$LOGFILE"
echo "Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOGFILE"
echo "Log: $LOGFILE"
