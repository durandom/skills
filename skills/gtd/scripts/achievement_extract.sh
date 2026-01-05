#!/bin/bash
# Extract achievements for quarterly review

set -euo pipefail

QUARTER=${1:-""}

if [ -z "$QUARTER" ]; then
  echo "Usage: $0 <quarter>"
  echo "Example: $0 Q4-2025"
  exit 1
fi

BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}🎯 Achievements for $QUARTER${NC}"
echo "═══════════════════════════════════════"
echo ""

# Get all achievements for the quarter
ACHIEVEMENTS=$(gh issue list \
  --assignee "@me" \
  --label "type/achievement" \
  --milestone "$QUARTER" \
  --state all \
  --json number,title,body,labels,closedAt,url \
  --limit 200)

if [ "$ACHIEVEMENTS" = "[]" ]; then
  echo "No achievements found for milestone: $QUARTER"
  echo ""
  echo "Available milestones:"
  gh api repos/:owner/:repo/milestones --jq '.[] | "  - \(.title)"'
  exit 0
fi

# Group by area and format for career review
for area in career architecture plugins customers ai-tooling documentation; do
  AREA_ACHIEVEMENTS=$(echo "$ACHIEVEMENTS" | jq -r --arg area "area/$area" '
    map(select(.labels | map(.name) | contains([$area]))) |
    if length > 0 then . else empty end
  ')

  if [ -n "$AREA_ACHIEVEMENTS" ] && [ "$AREA_ACHIEVEMENTS" != "null" ]; then
    case $area in
      career)         SECTION="Career Development & Mentorship" ;;
      architecture)   SECTION="Technical Leadership & Architecture" ;;
      plugins)        SECTION="Plugin Ecosystem & Marketplace" ;;
      customers)      SECTION="Customer Engagement & Support" ;;
      ai-tooling)     SECTION="AI Initiatives & Innovation" ;;
      documentation)  SECTION="Documentation & Knowledge Sharing" ;;
    esac

    echo -e "${GREEN}## ${SECTION}${NC}"
    echo ""

    echo "$AREA_ACHIEVEMENTS" | jq -r '.[] |
      "- **\(.title)** [#\(.number)](\(.url))\n" +
      if .body != null and .body != "" then "  \(.body | split("\n") | map("  " + .) | join("\n"))\n" else "" end +
      if .closedAt != null then "  *Completed: \(.closedAt | split("T")[0])*\n" else "" end
    '
    echo ""
  fi
done

# Summary stats
TOTAL=$(echo "$ACHIEVEMENTS" | jq 'length')
echo "────────────────────────────────────────"
echo -e "${BLUE}📊 Summary: ${TOTAL} achievements in ${QUARTER}${NC}"
