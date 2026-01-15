# Skill Discovery: Problem Domain

**Status**: Brainstorming
**Date**: 2026-01-15

## Problem Statement

Layton claims skill-agnostic design (FR-001, FR-002) but has implicit tight coupling:

```python
# gather.py:89 - hardcoded assumption
subprocess.run([str(cli_path), "list", "--json"])

# capture.py:54 - hardcoded assumption
subprocess.run([str(cli_path), "capture", text, "--json"])

# discovery.py:91 - keyword heuristic
if "capture" in content.lower():
    return True
```

**Consequence**: New skills must reverse-engineer these patterns from source code. This contradicts the spec's intent.

## Key Insight: Agentic Context

We're running in an **agentic context**. Claude can:

- Read a skill's SKILL.md to understand how it works
- Adapt queries based on what it learns
- Remember successful patterns for next time

This changes the integration paradigm:

| Traditional | Agentic |
|-------------|---------|
| Skills must implement protocol | Skills must document what they do |
| Rigid interface contract | Natural language documentation |
| Compile-time validation | Runtime understanding |

## Proposed Model: Learn and Cache Recipes

### First Interaction

```
User: "hey i need to check my jiras"

Claude:
  1. Discovers Jira skill via native skill system
  2. Reads skills/jira/SKILL.md
  3. Understands: "use `jira issues --assignee=@me` to list tickets"
  4. Executes query, returns results

Layton:
  5. Stores "recipe" - how to query Jira for this user's context
```

### Subsequent Interactions

```
User: "check my jiras"

Layton:
  1. Finds recipe for "jira discovery"
  2. Either:
     a) Executes command directly (fast, deterministic)
     b) Presents recipe to Claude (context-aware adaptation)
```

## Recipe Structure (Strawman)

```yaml
# .layton/recipes/jira.yaml
skill: jira
learned_from: skills/jira/SKILL.md
learned_at: 2026-01-15T10:30:00Z

triggers:
  - "check my jiras"
  - "jira status"
  - "my tickets"
  - "what's blocked"

commands:
  list_my_issues:
    command: "jira issues --assignee=@me --status=open --json"
    output: json
    use_when: "user wants to see their tickets"

  list_blocked:
    command: "jira issues --status=blocked --json"
    use_when: "user asks about blockers"

capture:
  command: "jira create --type=task --summary='{{text}}'"
  use_when: "user wants to create a ticket"
```

## Execution Modes

### Option A: Direct Execution

```
Recipe found → run command directly via CLI
```

- Fast, predictable
- No AI overhead
- Less context-aware

### Option B: Recipe-Guided AI

```
Recipe found → present to Claude with user context → Claude adapts
```

- Context-aware ("especially blocked ones for API project")
- Slower than direct, faster than re-reading full SKILL.md
- Claude can combine recipe knowledge with current request

### Option C: Hybrid

- Simple queries: Direct execution
- Complex/contextual queries: Claude with recipe guidance

## Recipe Lifecycle

```
LEARN           USE             REFRESH
─────────────────────────────────────────
First query     Fast path       Skill changed?
Read SKILL.md   Use recipe      Command failed?
Store recipe                    User: "relearn"
```

**Refresh triggers to consider:**

- SKILL.md modified since recipe creation
- Command returns error
- User explicitly requests refresh
- Recipe age threshold

## Open Questions

### Q1: Recipe Granularity

- One recipe per skill?
- One recipe per command/intent?
- One recipe per user interaction pattern?

### Q2: Storage Location

- `.layton/recipes/` - alongside config
- In Beads as `layton:recipe` type - versioned, searchable
- In memory only - per-session, no persistence

### Q3: Who Writes Recipes?

- Layton (AI) generates from SKILL.md understanding
- User can manually create/edit
- Both (AI proposes, user refines)

### Q4: Recipe vs. SKILL.md Relationship

- Recipe is a "compiled" subset of SKILL.md
- Recipe captures user-specific patterns (my assignee, my projects)
- SKILL.md is source of truth, recipe is cache

### Q5: Cross-Skill Recipes

Can a recipe span multiple skills?

```yaml
# Recipe for "morning briefing"
steps:
  - skill: calendar
    command: "calendar today --json"
  - skill: gtd
    command: "gtd daily --json"
  - skill: jira
    command: "jira issues --assignee=@me --status=blocked"
```

## Relationship to User Stories

From [user-stories.md](user-stories.md):

| Story | How Recipes Help |
|-------|------------------|
| A: Morning Briefing | Multi-skill recipe for "what's my day" |
| C: What's Next | Recipe with energy/time context |
| E: Cross-System Query | Recipe for entity search across skills |
| F: Smart Capture | Recipe for routing captures to right skill |

## Next Steps

1. Decide on execution mode (A/B/C)
2. Decide on storage location
3. Define recipe schema
4. Prototype with one skill (e.g., Jira or GTD)
5. Validate learning/refresh cycle
