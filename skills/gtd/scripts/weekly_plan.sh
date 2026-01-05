#!/bin/bash
# Weekly GTD planning - shows upcoming work grouped by area

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📅 Weekly Plan - Week of $(date +%Y-%m-%d)${NC}"
echo "════════════════════════════════════════"
echo ""

# Get this week's work (horizon/now and horizon/soon)
WEEK_ISSUES=$(gh issue list \
  --assignee "@me" \
  --label "horizon/now,horizon/soon" \
  --state open \
  --json number,title,labels,url \
  --limit 100)

# Group by area
for area in career architecture plugins customers ai-tooling documentation; do
  AREA_ISSUES=$(echo "$WEEK_ISSUES" | jq -r --arg area "area/$area" '
    map(select(.labels | map(.name) | contains([$area]))) |
    if length > 0 then . else empty end
  ')

  if [ -n "$AREA_ISSUES" ] && [ "$AREA_ISSUES" != "null" ]; then
    COUNT=$(echo "$AREA_ISSUES" | jq 'length')

    case $area in
      career)         ICON="🎯"; LABEL="Career" ;;
      architecture)   ICON="🏗️"; LABEL="Architecture" ;;
      plugins)        ICON="🔌"; LABEL="Plugins" ;;
      customers)      ICON="👥"; LABEL="Customers" ;;
      ai-tooling)     ICON="🤖"; LABEL="AI Tooling" ;;
      documentation)  ICON="📚"; LABEL="Documentation" ;;
    esac

    echo -e "${GREEN}${ICON} ${LABEL} (${COUNT} tasks)${NC}"

    echo "$AREA_ISSUES" | jq -r '.[] |
      "  #\(.number) \(.title)" +
      if (.labels | map(.name) | contains(["priority/urgent"])) then " 🔥"
      elif (.labels | map(.name) | contains(["priority/high"])) then " ⚡"
      else "" end
    '
    echo ""
  fi
done

# Projects overview (type/project)
PROJECTS=$(gh issue list \
  --assignee "@me" \
  --label "type/project" \
  --state open \
  --json number,title,url \
  --limit 50)

if [ -n "$PROJECTS" ] && [ "$PROJECTS" != "[]" ]; then
  COUNT=$(echo "$PROJECTS" | jq 'length')
  echo -e "${YELLOW}📦 Active Projects (${COUNT})${NC}"
  echo "$PROJECTS" | jq -r '.[] | "  #\(.number) \(.title)"'
  echo ""
fi

echo "────────────────────────────────────────"
echo -e "${BLUE}💡 Recommended Focus:${NC}"
echo "  1. Complete urgent items first"
echo "  2. Advance active projects"
echo "  3. Clear waiting items if unblocked"
