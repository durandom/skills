#!/bin/bash
# Create GTD labels for GitHub Issues

set -e  # Exit on error

echo "Creating GTD label structure..."

# Context labels (work mode)
echo "→ Context labels..."
gh label create "context/focus" --color "0E8A16" --description "Morning deep work (8am-1pm)" --force
gh label create "context/meetings" --color "0E8A16" --description "Afternoon synchronous (2-6pm)" --force
gh label create "context/async" --color "0E8A16" --description "Asynchronous communication" --force
gh label create "context/offsite" --color "0E8A16" --description "Quarterly travel, customer visits" --force

# Energy labels (cognitive load)
echo "→ Energy labels..."
gh label create "energy/high" --color "D4C5F9" --description "Needs context, deep thinking" --force
gh label create "energy/low" --color "E4E4E4" --description "Quick, routine, low overhead" --force

# Horizon labels (GTD time)
echo "→ Horizon labels..."
gh label create "horizon/now" --color "D93F0B" --description "This week" --force
gh label create "horizon/soon" --color "FBCA04" --description "This month" --force
gh label create "horizon/later" --color "C5DEF5" --description "Someday/maybe" --force
gh label create "horizon/waiting" --color "EDEDED" --description "Waiting for others" --force

# Area labels (PARA-aligned)
echo "→ Area labels..."
gh label create "area/career" --color "5319E7" --description "Career development" --force
gh label create "area/architecture" --color "5319E7" --description "Technical architecture" --force
gh label create "area/plugins" --color "5319E7" --description "Plugin ecosystem" --force
gh label create "area/customers" --color "5319E7" --description "Customer engagements" --force
gh label create "area/ai-tooling" --color "5319E7" --description "AI initiatives" --force
gh label create "area/documentation" --color "5319E7" --description "Documentation" --force
gh label create "area/team" --color "5319E7" --description "Team leadership" --force
gh label create "area/process" --color "5319E7" --description "Engineering processes" --force

# Priority labels
echo "→ Priority labels..."
gh label create "priority/urgent" --color "B60205" --description "Must do this week" --force
gh label create "priority/high" --color "D93F0B" --description "Important" --force
gh label create "priority/normal" --color "FBCA04" --description "Regular priority" --force
gh label create "priority/low" --color "C5DEF5" --description "Nice to have" --force

# Type labels
echo "→ Type labels..."
gh label create "type/project" --color "1D76DB" --description "Multi-step project" --force
gh label create "type/task" --color "1D76DB" --description "Single task" --force
gh label create "type/achievement" --color "0E8A16" --description "Career achievement" --force
gh label create "type/blocked" --color "B60205" --description "Blocked" --force

echo "✓ All labels created successfully!"
echo ""
echo "Label summary:"
echo "  - Context: 4 labels (focus, meetings, async, offsite)"
echo "  - Energy: 2 labels (high, low)"
echo "  - Horizon: 4 labels (now, soon, later, waiting)"
echo "  - Area: 8 labels (career, architecture, plugins, customers, ai-tooling, documentation, team, process)"
echo "  - Priority: 4 labels (urgent, high, normal, low)"
echo "  - Type: 4 labels (project, task, achievement, blocked)"
echo ""
echo "Total: 26 labels"
