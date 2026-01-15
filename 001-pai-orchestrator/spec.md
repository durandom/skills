# Feature Specification: Personal AI Orchestrator

**Feature Branch**: `001-pai-orchestrator`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "AI Personal Assistant for Knowledge Workers - A skill that coordinates other skills to manage information flow across task tracking, communication, calendar, and documentation sources"

## User Scenarios & Testing *(mandatory)*

> **See also**: [user-stories.md](user-stories.md) for concrete day-in-the-life scenarios showing actual orchestration flows with example outputs.

### User Story 1 - Morning Briefing (Priority: P1)

A knowledge worker starts their day and needs a consolidated view of everything relevant: calendar commitments, outstanding tasks prioritized by urgency, unread communications requiring attention, and context from recent meetings. The orchestrator synthesizes information from all connected skills and presents an actionable daily plan.

**Why this priority**: This is the foundational use case that demonstrates the core value proposition - reducing cognitive load by consolidating scattered information into one coherent briefing. Without this, the orchestrator has no primary purpose.

**Independent Test**: Can be tested by invoking the morning briefing and verifying it returns aggregated data from calendar, GTD tasks, and flagged communications with appropriate prioritization.

**Acceptance Scenarios**:

1. **Given** a new day has started and previous day's context exists, **When** user requests morning briefing, **Then** system presents calendar events, top-priority tasks, and items requiring attention in a unified view
2. **Given** calendar shows back-to-back meetings, **When** morning briefing runs, **Then** system identifies preparation needed for each meeting and suggests realistic task windows
3. **Given** GTD inbox has new items from overnight, **When** morning briefing runs, **Then** system surfaces inbox count and recommends processing time
4. **Given** no calendar events for the day, **When** morning briefing runs, **Then** system suggests focused work blocks aligned with high-energy task priorities

---

### User Story 2 - Adaptive Focus Management (Priority: P2)

During the workday, the user's context changes: meetings start/end, tasks complete, new urgent items arrive. The orchestrator tracks these state changes and proactively suggests what to focus on next, respecting the user's energy levels, current context (focus time vs. between-meetings), and stated priorities.

**Why this priority**: Builds on morning briefing by making the system useful throughout the day, not just at startup. Delivers continuous value rather than point-in-time snapshots.

**Independent Test**: Can be tested by simulating context changes (meeting ended, task completed) and verifying the system suggests appropriate next actions.

**Acceptance Scenarios**:

1. **Given** a meeting just ended, **When** user asks "what's next?", **Then** system reviews remaining calendar, outstanding tasks, and suggests next action with rationale
2. **Given** user completed a high-energy task, **When** requesting next focus, **Then** system considers energy depletion and may suggest a lower-energy task or break
3. **Given** an urgent item arrived during a meeting, **When** meeting ends and user checks in, **Then** system surfaces the urgent item with context on why it's urgent

---

### User Story 3 - Cross-System Intelligence (Priority: P2)

The user mentions something in one context (e.g., "follow up with Sarah about the API design") and the orchestrator connects this to relevant information across systems: Sarah's calendar availability, existing tickets/issues involving Sarah, recent meeting notes where the API was discussed, and related GTD tasks. Entity correlation uses semantic AI matching - "Sarah" contextually matches "Sarah Jones" or "S. Jones" without explicit mappings.

**Why this priority**: This delivers the "assistant that knows your world" experience - connecting dots the user shouldn't have to connect manually. Same priority as P2 because it's a parallel enhancement to focus management.

**Independent Test**: Can be tested by providing a query with named entities (using partial names or variations) and verifying the system returns correlated information from multiple sources.

**Acceptance Scenarios**:

1. **Given** user mentions a colleague's name, **When** asking about follow-ups, **Then** system surfaces recent meetings with that person, open tasks involving them, and pending communications
2. **Given** user mentions a project name, **When** asking for status, **Then** system aggregates relevant tickets, meeting notes, and tasks into a coherent summary
3. **Given** user captured a quick note yesterday, **When** that note becomes relevant to today's work, **Then** system surfaces it proactively with context

---

### User Story 4 - Weekly/Monthly Planning Support (Priority: P3)

Beyond daily operations, the user needs to step back and review progress against goals, plan upcoming weeks, and ensure projects are on track. The orchestrator supports these longer planning horizons by aggregating trends, highlighting stalled work, and facilitating reviews.

**Why this priority**: Important for sustained effectiveness but not required for day-to-day value. Can be deferred until core daily functionality is solid.

**Independent Test**: Can be tested by invoking weekly review and verifying it presents project status, completed vs. planned work, and items requiring attention.

**Acceptance Scenarios**:

1. **Given** a week has passed, **When** user initiates weekly review, **Then** system presents completed tasks, ongoing projects status, and items that slipped
2. **Given** a project has had no activity for 2 weeks, **When** running any review, **Then** system flags the stalled project for attention
3. **Given** quarterly goals exist, **When** running monthly review, **Then** system shows progress toward each goal with actionable recommendations

---

### User Story 5 - Skill Delegation with Context (Priority: P3)

When the user needs to perform a specific action (capture a task, process inbox, sync meeting notes), the orchestrator delegates to the appropriate specialized skill while maintaining context. The orchestrator knows which skill handles what and routes requests appropriately.

**Why this priority**: This is architectural plumbing that enables clean separation of concerns. Important for maintainability but users don't directly experience this as a distinct feature.

**Independent Test**: Can be tested by issuing various commands and verifying they route to correct skills with proper context preservation.

**Acceptance Scenarios**:

1. **Given** user says "capture: call dentist", **When** orchestrator processes this, **Then** it delegates to GTD skill's capture workflow with the text
2. **Given** user asks about PARA methodology, **When** orchestrator recognizes this as teaching request, **Then** it delegates to B4Brain skill
3. **Given** user asks to sync meeting notes, **When** orchestrator processes this, **Then** it invokes meeting-notes skill with appropriate parameters

---

### Edge Cases

- What happens when a connected skill is unavailable or returns an error?
  - Orchestrator continues with available information, clearly indicating what's missing
- How does system handle conflicting priorities from different sources?
  - User's explicit priorities override inferred priorities; system explains conflicts when detected
- What happens when there's no data from a source (e.g., empty calendar)?
  - System adapts presentation to focus on available information without placeholder noise
- How does system handle time zone changes or travel?
  - System uses user's configured location/timezone from AGENT.md as source of truth

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST function standalone using only its own state; external skills (calendar, GTD, meeting-notes) are optional enrichment layers that enhance but don't gate functionality
- **FR-002**: System MUST preserve loose coupling via native Skill infrastructure - reads target SKILL.md for context, invokes CLIs for operations, no custom integration code
- **FR-003**: System MUST track meta-state (when was each skill last queried, what is user's current focus context)
- **FR-004**: System MUST support multiple time horizons: daily (morning briefing), weekly (review), monthly (goal progress)
- **FR-005**: System MUST route specialized requests to appropriate underlying skills with context preservation
- **FR-006**: System MUST surface attention items based on: (1) time-based criteria (deadline proximity), and (2) explicit user markers (starred emails, GTD active/high-energy labels, flagged tasks)
- **FR-007**: System MUST adapt recommendations based on user's energy level and current context (focus time, between meetings, end of day)
- **FR-008**: System MUST maintain single source of truth principle - clearly indicate where authoritative data resides for each domain
- **FR-009**: System MUST detect available skills dynamically and adapt presentation accordingly (no skills = notepad mode; each skill adds capability layer)
- **FR-010**: System MUST support deterministic operations (archiving, formatting) separately from AI-driven operations (interpretation, recommendations)
- **FR-011**: All CLI operations MUST support progressive verbosity (default minimal, `--verbose` flag for diagnostic detail) enabling AI agent self-diagnosis on unexpected results
- **FR-012**: System MUST default to read-only operations; modifications require explicit user intent (not inferred from context)
- **FR-013**: Destructive operations (deleting tasks, removing calendar events, archiving data) MUST require explicit user confirmation before execution
- **FR-014**: System MUST provide `orchestrator doctor` CLI for validation of both Orchestrator State and Personal Configuration, with schema drift detection and auto-migration via hidden `--fix` flag (agentic CLI pattern)
- **FR-015**: System MUST support personal configuration covering three dimensions: (1) user preferences & workflows (operational), (2) assistant personality traits (tone, voice, verbosity), (3) interaction style (proactive clarifications, teaching mode, interactivity level)
- **FR-016**: Personal configuration MUST be discoverable through interaction OR explicitly configurable (not hardcoded in skill)
- **FR-017**: Personal configuration MUST be stored separately from skill definition (skill is shared; preferences are personal)
- **FR-020**: Workflow preferences MUST support prose/natural language instructions (not just structured JSON) to allow nuanced behavioral guidance like "bias toward high-energy tasks before noon" or "always highlight messages from Sarah"
- **FR-021**: System MUST support per-skill workflow customization through prose instructions that guide how each skill is queried and how results are prioritized
- **FR-022**: System MUST allow users to update preferences conversationally (e.g., "add Platform team to my tracked people") with explicit confirmation before writing to preferences file
- **FR-023**: System MUST support item-level attention tracking via Attention References - user can say "track JIRA-1234 for me" and Layton creates a reference bead with context
- **FR-024**: Attention References MUST store only reference pointers and Layton's annotations, NOT cached copies of external system data (secretary's notes model)
- **FR-025**: System MUST combine Attention References with live skill queries during synthesis - reference provides context ("you're tracking this"), skill provides current state
- **FR-026**: System MUST support meta-state tracking at skill level (when was this skill last queried) AND item level (when did I last check on JIRA-1234)
- **FR-027**: Users MUST be able to resolve/archive Attention References when items are no longer relevant ("stop tracking JIRA-1234" or "that's done now")
- **FR-018**: System MUST default to high-level summaries and support explicit zoom in/out for detail control (semantic zoom pattern)
- **FR-019**: System MUST request appropriate abstraction level when delegating queries to underlying skills, synthesizing responses at the user's current zoom level

### Key Entities

- **Orchestrator State**: Persistent JSON files with loose schema, validated by external `orchestrator doctor` CLI. Spans three temporal dimensions:
  - *Current context*: Active focus area, energy level, time of day, in-progress task
  - *History/Log*: Audit trail of completed work, skill interactions, decisions made
  - *Planning horizon*: Upcoming commitments, deadlines, goals across daily/weekly/monthly timeframes
  - *Schema evolution*: Handled via `doctor --fix` auto-migration, not embedded in skill prose
- **Unified View**: Aggregated presentation combining data from multiple skills for a specific purpose (briefing, review, focus suggestion)
- **Attention Item**: Something requiring user awareness, with source, urgency level, and recommended action. Computed at runtime from skill data and Attention References.
- **Attention Reference**: Layton's note about a specific item in an external system that the user wants to track. Stored in Beads as a **reference with annotations**, not a cached copy of the data. Contains:
  - *Reference pointer*: System name + ID + optional URL (e.g., `{system: "jira", id: "JIRA-1234"}`)
  - *Context/annotation*: Why this matters, user's notes (e.g., "Blocking release, promised Kim to check Monday")
  - *Tracking metadata*: Created date, optional reminder, status (tracking/resolved/deferred)
  - *Key principle*: Store the reference and Layton's context, NOT cached data from the source system
- **Context**: Current user state including time of day, recent activities, energy level, and active focus area
- **Personal Configuration**: User-specific settings split across two files:
  - *Structured settings* (`.layton/config.json`): Work hours, timezone, personality traits (verbosity/tone), interaction preferences (teaching mode, semantic zoom). Uses loose JSON schema validated by `orchestrator doctor` CLI.
  - *Behavioral instructions* (`.layton/preferences.md`): Prose/natural language workflow customizations - per-skill query preferences, people to track, prioritization rules, contextual behaviors. Interpreted by AI, not schema-validated.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can obtain a complete morning briefing in under 60 seconds that includes calendar, tasks, and attention items
- **SC-002**: User reduces context-switching overhead by 50% when transitioning between activities (measured by: baseline manual check ~60s → target with Layton ~30s to identify next action; validated via 10-interaction sample during pilot)
- **SC-003**: 90% of user queries about "what should I do next?" result in actionable recommendations without requiring follow-up questions (measured by: pilot user logs 20 queries, counts how many required clarification; target ≤2 of 20)
- **SC-004**: Cross-system queries (e.g., "what's happening with Project X?") return relevant information from all applicable sources in a single response
- **SC-005**: System provides useful baseline value with zero external skills configured; each skill integration adds measurable capability without breaking existing functionality
- **SC-006**: Weekly reviews surface stalled projects and slipped commitments that would otherwise go unnoticed

## Clarifications

### Session 2026-01-13

- Q: Does orchestrator state persist between sessions, and what is included? → A: Yes, state persists and includes three temporal dimensions: current context, history/log (audit trail), and planning horizon (forward-looking commitments). Storage mechanism deferred to planning phase.
- Q: How does orchestrator communicate with underlying skills? → A: Via native Claude Code Skill infrastructure - reads target skill's SKILL.md for instructions (Level 2), invokes skill CLIs with JSON output for deterministic operations (Level 3). No custom integration code; leverages progressive disclosure architecture.
- Q: How are entities (people, projects) matched across different systems? → A: Semantic matching via AI interpretation. Claude correlates entities contextually (e.g., "Sarah" in GTD task matches "Sarah Jones" in calendar) without requiring explicit mappings.
- Q: What criteria define urgency for attention items? → A: Time-based + explicit markers. Items surface when: (1) deadline within configurable threshold, or (2) user-flagged (starred emails, GTD "active" label, explicit priority markers).
- Q: What observability strategy for debugging? → A: AI-native progressive verbosity. Default: minimal output (just works). On unexpected results: agent retries with increased verbosity flag (e.g., `--verbose`). No persistent file logging; verbosity is on-demand.
- Q: What security/privacy boundaries apply? → A: Behavioral safety over data protection. Principle: "Read by default, write with intent, destroy with approval." Orchestrator handles personal data (acknowledged) but primary concern is preventing unintended cascading modifications across coordinated skills. Read operations are default; modifications require explicit intent; destructive actions require user confirmation.
- Q: How should orchestrator handle schema for its internal state? → A: JSON files + external validation/doctor script. State stored as loose JSON; a separate `orchestrator doctor` CLI command validates structure, detects schema drift, and offers `--fix` for auto-migration. Schema evolution is a script concern, not embedded in skill prose (per extract-deterministic pattern).
- Q: What is the minimum skill set for orchestrator to function? → A: None - orchestrator is skill-agnostic. Like a human secretary with just a notepad, core value is tracking and surfacing information. Skills (GTD, calendar, meeting-notes, PARA) are optional enrichment layers that add capability but aren't required. Each integration enhances but doesn't gate functionality.
- Q: How does orchestrator adapt to personal requirements? → A: Three-dimensional personal configuration: (1) user preferences & workflows (operational - how things work), (2) personality traits (tone, voice, verbosity), (3) interaction style (proactive clarifications, teaching mode, interactivity). Discoverable through interaction or explicitly configurable. Storage location deferred to planning phase.
- Q: How does orchestrator handle abstraction levels? → A: Semantic zoom pattern applies bidirectionally: (1) orchestrator defaults to high-level summaries with explicit zoom in/out support for users, (2) orchestrator requests appropriate abstraction level when delegating to skills and synthesizes at user's current zoom level.
- Q: What schema approach for Personal Configuration? → A: Loose JSON schema, consistent with Orchestrator State. Validated by same `orchestrator doctor` CLI with drift detection and `--fix` auto-migration.
- Q: How does orchestrator determine user's energy level? → A: Personal configuration option (per FR-015). User configures preferred mechanism: explicit statements only, time-based heuristics, or hybrid. Implementation details deferred to planning phase.
- Q: Does orchestrator cache aggregated data from skills? → A: No data caching - always query skills live (single source of truth per FR-008). However, meta-state (last query timestamps per skill) IS tracked per FR-003, enabling "since last check" intelligence (e.g., "3 new emails since 2 hours ago").
- Q: How are context states (focus time, between meetings, end of day) determined? → A: Derived from available signals. "Between meetings" from calendar events, "end of day" from work schedule in personal config (loose schema), "focus time" from user statement or absence of imminent calendar events. No explicit declaration required.
- Q: To meet the <60s briefing target (SC-001), how should the orchestrator handle multiple skill queries? → A: Strategy (concurrent vs sequential) is explicitly deferred to the planning phase.

### Session 2026-01-13 (Plan Comparison)

- Q: Which concurrency strategy should be used for parallel skill queries? → A: Sequential execution (start simple, optimize later if 60s target at risk)
- Q: Should we add `ask` and `capture` commands from Gemini's alternate plan? → A: Yes, both - NL queries across skills + rapid capture delegation
- Q: How are `ask` and `capture` implemented? → A: `capture` is CLI (`layton note`) since routing is deterministic. `ask` is SKILL.md workflows (morning-briefing, cross-system-query, etc.) since NL queries require AI synthesis - probabilistic work that doesn't belong in CLI.
- Q: Where should config/state be stored? → A: Repo-local `.layton/` directory (not home directory) - skill executes in target repo, keeps data portable and gitignore-able

## Assumptions

- User context (location, timezone, email) is available via AGENT.md
- **Optional enrichments** (none required for basic functionality):
  - Calendar access via MCP (Google Calendar) - adds time-aware suggestions
  - GTD skill (GitHub Issues backend) - adds task-aware prioritization
  - meeting-notes skill (Gemini integration) - adds meeting context
  - PARA skill - adds area/project correlation
- **Testing note**: US1-US5 acceptance scenarios reference external skills (calendar, GTD) for realistic examples. Tests use mock skill fixtures returning canned JSON responses; no real skill implementations are required for test coverage.

## Scope Boundaries

### In Scope

- Coordination and aggregation of existing skills
- Daily, weekly, and monthly planning support
- Proactive attention management
- Context-aware focus recommendations
- Cross-system entity correlation (people, projects, topics)

### Out of Scope

- Direct integration with new external systems (Jira, Slack, etc.) - these would be separate skills
- Real-time notification/push capabilities - this is a pull/query model
- Learning user preferences over time - initial version uses explicit configuration
- Multi-user coordination or delegation to other people

## References

- [user-stories.md](user-stories.md) - Concrete day-in-the-life scenarios with example orchestration flows and outputs
- [ADR-0001: bd prime as source of truth](https://github.com/steveyegge/beads/blob/main/claude-plugin/skills/beads/adr/0001-bd-prime-as-source-of-truth.md) - Architectural inspiration for single-source-of-truth and progressive disclosure patterns
- [Anthropic Agent Skills Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview) - Native Skill infrastructure leveraged for skill coordination
- [Semantic Zoom Recipe](recipes/semantic-zoom.md) - Pattern for controlling abstraction level in AI interactions; informs FR-018/FR-019
