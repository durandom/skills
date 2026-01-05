---
name: gtd
description: GitHub-based GTD (Getting Things Done) task management with context, energy, and achievement tracking for personal productivity.
---

# GTD Skill

Personal task and achievement tracking using GitHub Issues and Projects.

## Quick Start

For simple queries, use `gh` directly:

```bash
gh issue list --assignee @me --label "horizon/now"    # Today's work
gh issue list --label "energy/low"                    # Quick tasks
gh issue list --label "type/achievement" --milestone "Q4-2025"  # Achievements
```

**⚠️ Issue creation errors?** See the [GitHub skill](../github/SKILL.md) for `gh issue create` error handling (escaping, label validation).

**⚠️ CRITICAL: Never create new labels!** The 26 GTD labels are fixed and complete. If a label doesn't exist, choose the closest existing label or ask the user.

## Scripts

Bundled scripts for common workflows:

- `scripts/daily.sh` - Today's work grouped by context/energy
- `scripts/quick.sh` - Quick/light tasks for between meetings
- `scripts/weekly_plan.sh` - Weekly planning view
- `scripts/achievement_extract.sh <quarter>` - Extract achievements for reviews
- `scripts/create-labels.sh` - One-time label setup
- `scripts/create-milestones.sh` - One-time milestone setup

## Label System (6 Dimensions)

**Context** (work mode):

- `context/focus` - Morning deep work (8am-1pm)
- `context/meetings` - Afternoon synchronous (2-6pm)
- `context/async` - Asynchronous communication
- `context/offsite` - Quarterly travel, customer visits

**Energy** (cognitive load):

- `energy/high` - Needs context, deep thinking
- `energy/low` - Quick, routine, low overhead

**Horizon** (GTD time):

- `horizon/now` - This week
- `horizon/soon` - This month
- `horizon/later` - Someday/maybe
- `horizon/waiting` - Waiting for others

**Area** (PARA-aligned):

- `area/career`, `area/architecture`, `area/plugins`, `area/customers`
- `area/ai-tooling`, `area/documentation`, `area/team`, `area/process`

**Priority**:

- `priority/urgent`, `priority/high`, `priority/normal`, `priority/low`

**Type**:

- `type/task` - Single actionable task
- `type/project` - Multi-step project
- `type/achievement` - Career achievement
- `type/blocked` - Can't proceed

## Common Workflows

**Morning routine:**

```bash
./scripts/daily.sh
# Shows: High energy focus → Light focus → Async → Blocked
```

**Between meetings:**

```bash
./scripts/quick.sh
# Shows: energy/low tasks (5-15 min each)
```

**Weekly planning:**

```bash
./scripts/weekly_plan.sh
# Shows: horizon/now + horizon/soon grouped by area
```

**Quarterly review:**

```bash
./scripts/achievement_extract.sh Q4-2025
# Extracts all achievements with evidence links
```

## References

- [label-taxonomy.md](references/label-taxonomy.md) - Complete label reference
- [docs/gtd.md](../../../docs/gtd.md) - Full system documentation

## Tips

- Use scripts over raw `gh` commands for better formatting
- Don't over-label: 3-4 labels per issue is enough
- Energy ≠ time: Quick task can be energy/high if it needs context
- Always add evidence links to achievements (JIRA, Slack, Docs)
- Morning = focus work, afternoon = meetings
