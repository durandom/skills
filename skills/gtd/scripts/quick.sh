#!/bin/bash
# Show quick/light tasks (between meetings, low energy)

echo "⚡ Quick Tasks (5-15 minutes)"
echo "============================"
echo ""

gh issue list --assignee @me \
  --label "energy/low,horizon/now" \
  --state open \
  --limit 15 \
  --json number,title,labels \
  --template '{{range .}}#{{.number}} {{.title}}{{"\n"}}{{end}}'
