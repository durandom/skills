---
name: gtd
description: Query GTD task management for active tasks, inbox status, and project progress
source: skills/gtd/SKILL.md
---

## Commands

Run from repo root. The GTD CLI manages tasks following Getting Things Done methodology.

```bash
GTD="./.claude/skills/gtd/scripts/gtd"

# Get inbox status (items needing clarification)
$GTD inbox

# List active next actions
$GTD list --status active --horizon action

# List focus work (high energy deep work)
$GTD list --context focus --energy high --status active

# List async tasks (email, messages, low-energy)
$GTD list --context async --status active

# List waiting-for items
$GTD list --status waiting

# Get project overview with progress
$GTD projects

# Daily review summary (comprehensive)
$GTD daily
```

## What to Extract

### From `inbox`

- **Inbox count**: Number of items needing clarification
- **Oldest item**: How long items have been sitting (staleness indicator)
- If inbox > 5 items, suggest processing before focus work

### From `list --status active`

- **Active action count**: Total actionable tasks
- **By context**: How many focus/async/meetings/offsite tasks
- **High energy available**: Tasks suitable for peak hours

### From `list --status waiting`

- **Waiting count**: Items blocked on others
- **Stale waiting items**: Anything waiting > 1 week needs follow-up

### From `projects`

- **Open projects count**: Active initiatives
- **Projects without actions**: Need next action defined
- **Projects near due date**: May need attention

### From `daily`

- **Morning focus recommendations**: Pre-filtered for context
- **Review status**: Whether reviews are current

## Key Metrics

| Metric | Meaning | Alert Threshold |
|--------|---------|-----------------|
| Inbox count | Unclarified items | > 10 = system untrusted |
| Active actions | Available work | < 5 = may need capture |
| Waiting items | Blocked tasks | > 10 = too much delegated |
| Focus tasks | Deep work available | 0 = capture focus work |
| Projects without actions | Stuck projects | Any = needs next action |
| Oldest inbox item | System staleness | > 3 days = review needed |
