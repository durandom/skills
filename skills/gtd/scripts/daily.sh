#!/bin/bash
# Show today's work grouped by context and energy

echo "🌅 Your Work for Today"
echo "====================="
echo ""

# High energy focus work
echo "🧠 High Energy Focus Work (morning 8am-1pm):"
gh issue list --assignee @me \
  --label "context/focus,energy/high,horizon/now" \
  --state open \
  --limit 10 \
  --json number,title \
  --template '{{range .}}  #{{.number}} {{.title}}{{"\n"}}{{end}}'
echo ""

# Light focus work
echo "📝 Light Focus Work (if time/energy permits):"
gh issue list --assignee @me \
  --label "context/focus,energy/low,horizon/now" \
  --state open \
  --limit 10 \
  --json number,title \
  --template '{{range .}}  #{{.number}} {{.title}}{{"\n"}}{{end}}'
echo ""

# Async work (anytime)
echo "📱 Async Work (anytime):"
gh issue list --assignee @me \
  --label "context/async,horizon/now" \
  --state open \
  --limit 10 \
  --json number,title \
  --template '{{range .}}  #{{.number}} {{.title}}{{"\n"}}{{end}}'
echo ""

# Meetings today
echo "📞 Meetings (check calendar for times)"
echo ""

# Communications check
echo "💬 Communications (ask Claude: \"check slack\")"
echo ""

# Blocked items
echo "⚠️  Blocked/Waiting:"
gh issue list --assignee @me \
  --label "type/blocked,horizon/waiting" \
  --state open \
  --limit 5 \
  --json number,title \
  --template '{{range .}}  #{{.number}} {{.title}}{{"\n"}}{{end}}'
