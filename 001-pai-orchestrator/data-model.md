# Data Model: Layton (Personal AI Assistant)

**Branch**: `001-pai-orchestrator` | **Date**: 2026-01-13

## Overview

Layton's data model is minimal by design:

- **State management** → Handled by [Beads](https://github.com/steveyegge/beads)
- **Personal configuration** → `.layton/config.json` (the only file Layton manages)
- **Skill data** → Queried live from skills via CLI subprocess calls

---

## State Management: Beads

Layton does NOT maintain custom state files. All state is managed by Beads:

| State Type | Where Stored | Example |
|------------|--------------|---------|
| Current focus | Beads | "Working on API design" |
| In-progress task | Beads | Linked to GTD task bead |
| Interaction history | Beads | Audit trail of briefings, queries |
| Planning horizon | Beads | Upcoming deadlines as beads |
| **Attention References** | Beads | Items user asked Layton to track |
| **Meta-state** | Beads | When each skill/item was last checked |

**Why Beads:**

- Git-backed (version controlled, mergeable)
- Designed for AI agent workflows
- Handles schema evolution automatically
- No custom migration scripts needed

---

## Attention References: Secretary's Notepad

Attention References are Layton's notes about specific items in external systems. They follow the **secretary's notepad model**: store references and annotations, NOT cached copies of data.

### The Principle

| Store (Secretary's Notes) | Don't Store (Cache/Mirror) |
|---------------------------|---------------------------|
| Reference to JIRA-1234 | Copy of ticket title, description |
| "Blocked on QA, check Monday" | Current ticket status |
| When I last looked at it | Full ticket history |
| My commitment about it | Assignee, labels, comments |

### Bead Structure

```json
{
  "type": "layton:attention",
  "reference": {
    "system": "jira",
    "id": "JIRA-1234",
    "url": "https://jira.example.com/browse/JIRA-1234"
  },
  "context": "Blocking release - promised Kim I'd check Monday",
  "created_at": "2026-01-10T14:00:00Z",
  "last_checked": "2026-01-12T09:00:00Z",
  "remind_at": "2026-01-13T09:00:00Z",
  "status": "tracking"
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Always `"layton:attention"` |
| `reference.system` | Yes | Source system name (jira, email, slack, etc.) |
| `reference.id` | Yes | ID in the source system |
| `reference.url` | No | Direct link to the item |
| `context` | No | Why this matters, user's notes |
| `created_at` | Yes | When tracking started |
| `last_checked` | No | When Layton last queried this item |
| `remind_at` | No | Optional reminder time |
| `status` | Yes | `tracking`, `resolved`, `deferred` |

### Status Lifecycle

```
User: "Track JIRA-1234 for me"
     │
     ▼
┌─────────────┐
│  tracking   │ ← Active attention
└─────┬───────┘
      │
      ├── User: "That's done" ──────────► resolved (archived)
      │
      └── User: "Defer that" ──────────► deferred (hidden from daily, shown in weekly)
```

### Flow: How Attention References Work

```
1. CAPTURE
   User: "Keep an eye on JIRA-1234, it's blocking the release"
   → Layton creates attention bead with context

2. SYNTHESIS (during briefing)
   - Query Jira skill → gets fresh JIRA-1234 data
   - Query Beads → finds attention reference for JIRA-1234
   - Combine: "JIRA-1234 (you're tracking this) - still blocked, 3 days now"

3. PROACTIVE SURFACING
   - Attention references with remind_at trigger reminders
   - Items tracked >N days without resolution get highlighted

4. RESOLUTION
   User: "JIRA-1234 is done"
   → Layton marks bead status: resolved
```

### Meta-State: Skill-Level Timestamps

Separate from item-level Attention References, Layton tracks when each skill was last queried:

```json
{
  "type": "layton:meta",
  "skill_timestamps": {
    "jira": "2026-01-13T08:00:00Z",
    "email": "2026-01-13T10:30:00Z",
    "gtd": "2026-01-13T08:00:00Z"
  }
}
```

This enables "since last check" intelligence:

- "3 new emails since you last checked (2 hours ago)"
- "JIRA-1234 was updated since yesterday"

---

## Personal Configuration

Layton uses two files for personalization:

| File | Purpose | Format |
|------|---------|--------|
| `.layton/config.json` | Structured settings | JSON (loose schema) |
| `.layton/preferences.md` | Behavioral instructions | Prose/Markdown |

**Rule of thumb**: Settings → JSON. Instructions → Prose.

---

### Config File

**Storage:** `.layton/config.json` (repo-local, gitignore-able)

**Purpose:** Structured settings that affect Layton's behavior (FR-015, FR-016, FR-017)

### Schema

```json
{
  "$schema": "layton-config-v1",
  "work_schedule": {
    "start": "HH:MM",
    "end": "HH:MM"
  },
  "timezone": "IANA timezone string",
  "personality": {
    "verbosity": "terse | normal | verbose",
    "tone": "professional | casual | friendly",
    "humor": boolean,
    "explanation_level": "concise | detailed | teaching"
  },
  "interaction": {
    "proactive_clarification": boolean,
    "teaching_mode": boolean,
    "semantic_zoom_default": "summary | detail"
  }
}
```

### Example

```json
{
  "$schema": "layton-config-v1",
  "work_schedule": {
    "start": "09:00",
    "end": "17:00"
  },
  "timezone": "America/Los_Angeles",
  "personality": {
    "verbosity": "terse",
    "tone": "professional",
    "humor": false,
    "explanation_level": "concise"
  },
  "interaction": {
    "proactive_clarification": true,
    "teaching_mode": false,
    "semantic_zoom_default": "summary"
  }
}
```

### Defaults

Used when config file is missing:

```json
{
  "work_schedule": {
    "start": "09:00",
    "end": "17:00"
  },
  "timezone": "UTC",
  "personality": {
    "verbosity": "normal",
    "tone": "professional",
    "humor": false,
    "explanation_level": "concise"
  },
  "interaction": {
    "proactive_clarification": true,
    "teaching_mode": false,
    "semantic_zoom_default": "summary"
  }
}
```

### Validation Rules

| Field | Rule |
|-------|------|
| `work_schedule.start` | Must be < `work_schedule.end` |
| `timezone` | Must be valid IANA timezone |
| `personality.verbosity` | Must be one of: terse, normal, verbose |
| `personality.tone` | Must be one of: professional, casual, friendly |
| `interaction.semantic_zoom_default` | Must be one of: summary, detail |

---

### Preferences File

**Storage:** `.layton/preferences.md` (repo-local, gitignore-able)

**Purpose:** Natural language instructions that customize Layton's behavior - like a personal CLAUDE.md overlay for the orchestrator.

**Why prose instead of JSON:**

- Workflow preferences are often nuanced ("bias toward high-energy before noon")
- AI interprets prose naturally - no schema translation needed
- Users can express complex conditions ("ignore newsletters unless weekly review")
- Easy to edit without knowing JSON syntax

### Example Structure

```markdown
# My Layton Preferences

## Email Handling
- Only surface starred messages by default
- Always highlight anything from Sarah Chen or VP-level
- Ignore newsletters unless doing weekly review

## Morning Routine
- Lead with calendar - I'm time-oriented
- Warn about prep time for back-to-back meetings
- Bias toward high-energy tasks before noon
- After 3pm, suggest lighter work

## Jira Priorities
- Focus on release-blocking tickets
- Deprioritize backlog grooming (except Fridays)
- Tickets blocked >3 days = urgent

## People I Track
- Sarah Chen (skip-level) - always surface her messages
- Kim (budget owner) - flag any docs awaiting my response
- Platform team - monitor for API-related updates

## Weekly Review
- Check Sarah response time (<48 hours)
- Flag stalled projects (no activity 5+ days)
- Show quarterly goals progress
```

### How Layton Uses Preferences

1. SKILL.md workflow reads `preferences.md` at startup
2. Instructions guide synthesis decisions (what to highlight, how to prioritize)
3. Preferences can reference skills by name - Layton passes context to skill queries
4. User can update preferences conversationally: "Add Platform team to my tracked people"

### Config vs. Preferences Decision Guide

| Goes in `config.json` | Goes in `preferences.md` |
|-----------------------|--------------------------|
| Work hours (09:00-17:00) | "Bias toward high-energy before noon" |
| Timezone (America/LA) | "Always mention Sarah's messages" |
| Verbosity (terse/verbose) | "Lead with calendar in briefings" |
| Teaching mode (on/off) | "Ignore newsletters unless weekly review" |
| Semantic zoom default | "If blocked >3 days, mark as urgent" |

### Validation

`layton doctor` checks:

- File exists (warns if missing, not an error)
- File is valid markdown (parseable)
- No validation of *content* - prose is interpreted by AI

---

## Runtime Data (Not Persisted)

These structures exist only during SKILL.md workflow execution:

### Gathered Skill Data

Output of `layton gather --json`:

```json
{
  "success": true,
  "timestamp": "ISO8601",
  "skills_available": ["skill-name", "..."],
  "skills_queried": ["skill-name", "..."],
  "data": {
    "skill-name": { /* raw skill CLI output */ }
  }
}
```

### Temporal Context

Output of `layton context --json`:

```json
{
  "timestamp": "ISO8601",
  "time_of_day": "morning | midday | afternoon | evening | night",
  "day_of_week": "monday | ... | sunday",
  "work_hours": boolean,
  "timezone": "IANA timezone string"
}
```

---

## What's NOT in the Data Model

These entities from the original spec are handled elsewhere:

| Original Entity | Now Handled By |
|-----------------|----------------|
| Orchestrator State | Beads |
| Unified View | Generated at runtime by SKILL.md workflows |
| Attention Item | Computed by SKILL.md workflows from skill data |
| Context | Computed by `layton context` CLI + SKILL.md interpretation |

---

## Directory Structure

```
.layton/                  # Repo-local (gitignore-able)
├── config.json           # Structured settings (JSON)
└── preferences.md        # Behavioral instructions (prose)

.beads/                   # State management
└── (managed by Beads)    # Focus, context, history as beads
```
