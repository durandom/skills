# Layton: Planning Session Summary

**Date**: 2026-01-15
**Status**: Exploration Complete → Ready for Stage 0
**Source**: `001-pai-orchestrator/` planning documents

---

## Context

Reviewed the comprehensive planning documents from a previous session:

| Document | Purpose |
|----------|---------|
| `spec.md` | Feature specification with 27 functional requirements |
| `plan.md` | Implementation plan with architecture diagrams |
| `user-stories.md` | 8 concrete usage scenarios (Stories A-H) |
| `data-model.md` | Config schema and state management approach |
| `skill-discovery.md` | Brainstorming on skill-agnostic design |
| `quickstart.md` | Usage guide |
| `research.md` | Technical decisions (R1-R5) |
| `contracts/cli-contract.md` | CLI command specifications |

---

## Critical Review Findings

### Issues with Original Plan

1. **Ambitious Scope** - User stories span GTD, Calendar, Jira, Email, Slack integration with cross-system entity correlation. Easily 6+ months if done at once.

2. **"Skill-Agnostic" Claim vs Reality** - Spec claims skill-agnostic design (FR-001, FR-002) but user stories assume specific skills exist. `skill-discovery.md` acknowledged: "Layton claims skill-agnostic design but has implicit tight coupling."

3. **Recipe System Underspecified** - Marked "Status: Brainstorming" but fundamental to making Layton useful without hardcoded skill knowledge.

4. **Original CLI Too Thick** - Proposed `layton track/untrack/watched` commands would replicate Beads functionality.

---

## Key Insight: The Secretary Analogy

Elizabeth Layton was Churchill's wartime secretary. The analogy clarifies what goes where:

```
┌─────────────────────────────────────┐   ┌─────────────────────────────┐
│      HER NOTEPAD (Beads)            │   │   HER FILING CABINET        │
│                                     │   │      (.layton/)             │
│  "What's happening RIGHT NOW"       │   │                             │
│                                     │   │  "What I've LEARNED about   │
│  • Items being tracked              │   │   how the user works"       │
│  • Current focus                    │   │                             │
│  • When I last checked things       │   │  • Work schedule            │
│  • Interaction history              │   │  • Personality preferences  │
│                                     │   │  • Behavioral instructions  │
│  [Temporal, mutable, working state] │   │  • Skill recipes            │
│                                     │   │                             │
│                                     │   │  [Stable, rarely changes]   │
└─────────────────────────────────────┘   └─────────────────────────────┘
```

### Notepad vs Filing Cabinet

| Notepad (Beads) | Filing Cabinet (.layton/) |
|-----------------|---------------------------|
| Frequently written/erased | Rarely updated |
| Time-sensitive | Institutional knowledge |
| Mutable working state | Stable configuration |
| "What am I watching?" | "How does user work?" |
| Per-item tracking | Per-pattern learning |

---

## Revised Architecture

### Core Decision: Beads is Non-Negotiable

Beads is the "brain and notepad" of Mrs. Layton. It's a full-fledged git-based issue tracker designed for AI agents with:
- Typed dependencies with semantics
- Deterministic ready-work detection
- Branch-scoped task memory
- AI-resolvable conflicts
- Agent-native APIs (`--json`, MCP server)

  The Secretary Mental Model

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                     MRS. LAYTON'S WORKSPACE                                  │
  │                                                                              │
  │  ┌─────────────────────────────────────┐   ┌─────────────────────────────┐  │
  │  │         HER NOTEPAD (Beads)         │   │    HER FILING CABINET       │  │
  │  │                                     │   │      (.layton/)             │  │
  │  │  "What's happening RIGHT NOW"       │   │                             │  │
  │  │                                     │   │  "What I've LEARNED about   │  │
  │  │  • Churchill asked me to track      │   │   how Churchill works"      │  │
  │  │    the response from Stalin         │   │                             │  │
  │  │  • Reminder: Ask about tea at 3pm   │   │  • He takes tea at 3pm      │  │
  │  │  • Currently drafting: memo to FDR  │   │  • He prefers terse updates │  │
  │  │  • Last checked mail: 2 hours ago   │   │  • Always mention Sarah's   │  │
  │  │                                     │   │    messages first           │  │
  │  │  [She writes, crosses out, updates] │   │  • Morning = high energy    │  │
  │  │  [Temporal, mutable, working state] │   │                             │  │
  │  │                                     │   │  [Stable, rarely changes]   │  │
  │  └─────────────────────────────────────┘   └─────────────────────────────┘  │
  │                                                                              │
  │  ┌─────────────────────────────────────┐   ┌─────────────────────────────┐  │
  │  │      HER HEAD (SKILL.md/Claude)     │   │   THE OFFICE (Skills)       │  │
  │  │                                     │   │                             │  │
  │  │  "Judgment, synthesis, anticipation"│   │  "Departments she calls"    │  │
  │  │                                     │   │                             │  │
  │  │  • Interprets what Churchill needs  │   │  • War Office (GTD)         │  │
  │  │  • Decides what to surface when     │   │  • Foreign Office (Jira)    │  │
  │  │  • Knows when to interrupt vs wait  │   │  • Scheduling (Calendar)    │  │
  │  │  • Synthesizes across departments   │   │  • Communications (Email)   │  │
  │  │                                     │   │                             │  │
  │  │  [AI judgment - probabilistic]      │   │  [External systems]         │  │
  │  └─────────────────────────────────────┘   └─────────────────────────────┘  │
  │                                                                              │
  └─────────────────────────────────────────────────────────────────────────────┘

  ---
  What Goes Where (Revised)
  ┌─────────────────────────┬────────────────────────┬─────────────────────────────────────┬────────────────────────────────────────────┐
  │          What           │         Where          │                 Why                 │                  Analogy                   │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Attention References    │ Beads                  │ Active tracking, changes frequently │ "Track the Stalin response" on her notepad │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Current focus           │ Beads                  │ Working state, session-specific     │ "Currently drafting the FDR memo"          │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Meta-state timestamps   │ Beads                  │ "When did I last check..."          │ "Last looked at mail 2 hours ago"          │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Interaction history     │ Beads                  │ Audit trail of what happened        │ Pages in her notepad, chronological        │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Work schedule           │ .layton/config.json    │ Structured, rarely changes          │ "He works 9-5" - factual                   │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Personality settings    │ .layton/config.json    │ Structured preferences              │ "He prefers terse updates"                 │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Behavioral instructions │ .layton/preferences.md │ Learned patterns, nuanced           │ "Always mention Sarah first"               │
  ├─────────────────────────┼────────────────────────┼─────────────────────────────────────┼────────────────────────────────────────────┤
  │ Skill recipes           │ .layton/recipes/       │ How to talk to departments          │ "When calling War Office, ask for..."      │
  └─────────────────────────┴────────────────────────┴─────────────────────────────────────┴────────────────────────────────────────────┘
  ---
  The Notepad vs. Filing Cabinet Distinction

  NOTEPAD (Beads)                        FILING CABINET (.layton/)
  ─────────────────                      ─────────────────────────

  ✏️  Frequently written/erased           📁 Rarely updated
  ⏰  Time-sensitive                       🏛️  Institutional knowledge
  🔄  Mutable working state               📋 Stable configuration
  👁️  "What am I watching?"               🧠 "How does he work?"
  📝  Per-item tracking                    📊 Per-pattern learning

  Examples:                              Examples:
  • "JIRA-1234 - blocking release"       • "Morning = high energy tasks"
  • "Last checked Jira: 9am"             • "Sarah's messages = priority"
  • "Focus: API design doc"              • "Jira blocked >3 days = urgent"
  • "Reminder: Monday 9am"               • work_schedule: 09:00-17:00

  ---
  Thinking Through: What is a "Recipe"?

  The skill-discovery.md doc proposed recipes as "learned ways to talk to skills." In the secretary model:

  MRS. LAYTON'S ROLODEX OF DEPARTMENT CONTACTS
  ────────────────────────────────────────────

  When Churchill says...          Mrs. Layton knows to...
  ─────────────────────────       ───────────────────────
  "What's happening in Burma?"    → Call War Office, ask for "Burma desk,
                                    active operations, briefing level"

  "Check on the Stalin letter"    → Call Foreign Office, ask for
                                    "correspondence, Stalin, pending"

  "My schedule today"             → Call Scheduling, ask for
                                    "today's appointments, include prep notes"

  These are learned patterns - not hardcoded, but discovered through experience. They live in the filing cabinet (.layton/recipes/) because they're stable institutional knowledge, not active tracking.

  ---
  Revised Architecture with Clear Boundaries

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                         MRS. LAYTON'S WORLD                                  │
  ├─────────────────────────────────────────────────────────────────────────────┤
  │                                                                              │
  │   .beads/                              .layton/                              │
  │   ═══════                              ════════                              │
  │   HER NOTEPAD                          HER FILING CABINET                    │
  │                                                                              │
  │   layton:attention                     config.json                           │
  │   ├─ JIRA-1234 (tracking)              ├─ work_schedule                      │
  │   ├─ PR-847 (tracking)                 ├─ timezone                           │
  │   └─ Budget doc (deferred)             ├─ personality                        │
  │                                        └─ interaction                        │
  │   layton:focus                                                               │
  │   └─ "Working on API design"           preferences.md                        │
  │                                        ├─ ## Morning Routine                 │
  │   layton:meta                          ├─ ## People I Track                  │
  │   └─ skill_timestamps: {...}           └─ ## Jira Priorities                 │
  │                                                                              │
  │   layton:history                       recipes/                              │
  │   └─ [interaction log]                 ├─ gtd.yaml                           │
  │                                        ├─ jira.yaml                          │
  │                                        └─ calendar.yaml                      │
  │                                                                              │
  ├─────────────────────────────────────────────────────────────────────────────┤
  │                                                                              │
  │   SKILL.md (Her Head)                  CLI (Her Hands)                       │
  │   ══════════════════                   ═══════════════                       │
  │                                                                              │
  │   • Interprets intent                  • layton gather (call departments)    │
  │   • Synthesizes briefings              • layton context (check the clock)    │
  │   • Decides what to surface            • layton note (jot something down)    │
  │   • Applies persona voice              • layton track (add to notepad)       │
  │   • Uses recipes to guide queries      • layton config (update settings)     │
  │                                        • layton doctor (self-check)          │
  │                                                                              │
  └─────────────────────────────────────────────────────────────────────────────┘


### Layton Does NOT Wrap Beads

**Original plan**: `layton track`, `layton untrack`, `layton tracked` commands
**Revised**: Use `bd` directly - don't replicate the Beads CLI

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MRS. LAYTON - FINAL ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   BEADS (bd CLI)                       .layton/                              │
│   ══════════════                       ════════                              │
│   HER NOTEPAD + TASK SYSTEM            HER FILING CABINET                    │
│                                                                              │
│   Used directly, NOT wrapped:          config.json                           │
│                                        ├─ work_schedule                      │
│   bd add "Track JIRA-1234"             ├─ timezone                           │
│   bd add --blocks bd-xyz "..."         ├─ personality                        │
│   bd ready                             └─ interaction                        │
│   bd list --tag watching                                                     │
│   bd close bd-abc                      preferences.md                        │
│                                        └─ (behavioral instructions)          │
│   Layton uses Beads' native features:                                        │
│   • Tags for categorization            recipes/                              │
│   • Dependencies for blocking          ├─ gtd.yaml                           │
│   • Ready detection for "what's next"  └─ jira.yaml                          │
│   • --json for AI consumption                                                │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   SKILL.md (Her Head)                  CLI (Minimal)                         │
│   ══════════════════                   ═══════════════                       │
│                                                                              │
│   • Interprets user intent             • layton gather (query skills)        │
│   • Calls bd directly for state        • layton context (temporal)           │
│   • Calls skill CLIs for data          • layton config (settings)            │
│   • Synthesizes briefings              • layton doctor (health check)        │
│   • Routes captures to appropriate                                           │
│     skill (no layton note command)     NO: track, untrack, watched, note     │
│                                        (use bd directly / SKILL.md routing)  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Responsibility Split

| Need | Who Handles | How |
|------|-------------|-----|
| Track an item | **bd** | `bd add "Watch JIRA-1234" --tag watching` |
| List watched items | **bd** | `bd list --tag watching --json` |
| Mark done | **bd** | `bd close bd-xyz` |
| What's blocking? | **bd** | `bd ready --json` |
| Current focus | **bd** | `bd list --tag focus --json` |
| Query skills for data | **layton** | `layton gather --json` |
| Temporal context | **layton** | `layton context --json` |
| Personal settings | **layton** | `layton config show` |
| Health check | **layton** | `layton doctor` |
| Capture routing | **SKILL.md** | Decides which skill, calls its CLI |
| Synthesis/briefings | **SKILL.md** | Combines bd + skills + context |

### Key Principle

> **Layton is a synthesis layer, not a state management layer.**
> - **Beads** = State (what's being tracked, what's ready, history)
> - **Layton** = Intelligence (what does this mean, what should user do)
> - **Skills** = Domain data (GTD tasks, calendar events, Jira tickets)

---

## Decisions Made

| Question | Decision | Rationale |
|----------|----------|-----------|
| Beads dependency? | **Hard requirement** | It's the brain and notepad - non-negotiable |
| `layton track` command? | **No** - use `bd` directly | Avoids replicating Beads CLI |
| Recipe storage? | **`.layton/recipes/`** | Filing cabinet model; git for versioning |
| `layton note` command? | **No** - SKILL.md handles routing | Keep CLI minimal; routing is AI judgment |
| Attention References? | **Beads with tags** | `bd add ... --tag watching` |

---

## Implementation Stages

### Stage 0: Beads Foundation
- Verify `bd` CLI is installed and working
- Define Beads conventions for Layton:
  - Tags: `watching`, `focus`, `layton:*`
  - How to store skill meta-state
- `layton doctor` (checks bd availability)
- `layton context` (pure temporal, no dependencies)
- `layton config` (personal settings)

**Deliverable**: bd commands work, Layton can check health
**Test**: `bd add "test" --tag watching && bd list --tag watching`

### Stage 1: Skill Discovery + Gather
- `layton gather` (discover skills, invoke CLIs)
- Integration with ONE skill (GTD)
- Basic SKILL.md that can synthesize bd + skill data

**Deliverable**: `layton gather` returns GTD data
**Test**: `layton gather --json | jq '.data.gtd'`

### Stage 2: Morning Briefing Workflow
- SKILL.md morning-briefing workflow
- Combines: `bd list --tag watching` + `layton gather` + `layton context`
- Persona voice (Elizabeth Layton)

**Deliverable**: "What should I know?" works end-to-end
**Test**: Natural language query returns synthesized briefing

### Stage 3: Recipes + Multi-Skill
- `.layton/recipes/` for learned skill patterns
- Multiple skill aggregation
- Focus suggestion workflow

**Deliverable**: Recipes guide skill queries intelligently

### Stage 4+: Advanced Features
- Cross-system entity correlation
- Weekly/monthly reviews
- Conversational preference learning

---

## File Inventory

### What We're Building

```
skills/layton/
├── SKILL.md                  # AI workflows, persona, routing
├── references/
│   └── persona.md            # Elizabeth Layton background
├── workflows/
│   ├── morning-briefing.md
│   ├── focus-suggestion.md
│   └── capture-routing.md
└── scripts/
    ├── layton                # CLI entrypoint (thin, ~100 lines)
    └── laytonlib/            # Internal package
        ├── __init__.py
        ├── models.py         # Pydantic models
        ├── config.py         # Config loading
        ├── discovery.py      # Skill discovery
        └── services/
            ├── context.py    # Temporal context
            └── gather.py     # Skill query orchestration

.layton/                      # Per-repo, gitignore-able
├── config.json               # Structured settings
├── preferences.md            # Behavioral instructions (prose)
└── recipes/                  # Learned skill patterns
    └── (empty initially)

.beads/                       # Managed by Beads
└── (bd manages this)
```

### What We're NOT Building

- `layton track/untrack/watched` - use `bd` directly
- `layton note` - SKILL.md handles capture routing
- Custom state files - Beads handles all state
- Schema migrations - Beads handles evolution

---

## Next Steps

1. **Verify Beads**: Ensure `bd` CLI is available and working
2. **Start Stage 0**: Implement `layton doctor` and `layton context`
3. **Define Conventions**: Document how Layton uses Beads tags/types

---

## References

- Original planning: `001-pai-orchestrator/`
- Beads: https://github.com/steveyegge/beads
- Elizabeth Layton: https://en.wikipedia.org/wiki/Elizabeth_Nel
