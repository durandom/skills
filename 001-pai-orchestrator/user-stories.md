# Layton User Stories: Concrete Usage Scenarios

**Feature Branch**: `001-pai-orchestrator`
**Purpose**: Day-in-the-life scenarios showing how Layton orchestrates skills in practice

These stories complement the high-level user scenarios in [spec.md](spec.md) with concrete examples showing actual orchestration flows.

---

## Story A: Morning Briefing (The 60-Second Catchup)

> **"Layton, what's my day look like?"**

### What Layton Orchestrates

| Source | Query | What User Sees |
|--------|-------|----------------|
| **Calendar MCP** | Today's events | "3 meetings: standup (9am), 1:1 with Sarah (11am), API review (2pm)" |
| **GTD skill** | `gtd daily` output | "5 active tasks, 2 high-energy for morning" |
| **meeting-notes** | Recent meetings with action items | "2 open action items from yesterday's RHDH standup" |
| **Jira skill** | Assigned issues | "3 tickets in-progress, 1 blocked awaiting QA" |
| **Email skill** (future) | Flagged/unread | "7 unread, 2 flagged from VP" |
| **Slack skill** (future) | Unread DMs/mentions | "4 unreads, 1 urgent from #incidents" |

### Synthesized Output

```
Good morning! Here's your Monday:

CALENDAR (3 meetings, 4 hours blocked)
   09:00 Standup (prep: review PR #847)
   11:00 1:1 with Sarah - you owe her API spec feedback
   14:00 API Review - 90 min deep work before this

ATTENTION REQUIRED
   - JIRA-1234 blocked for 2 days (QA hasn't responded)
   - Action item from Friday: "Send SRE proposal to Kim"
   - VP email flagged: budget approval needed

RECOMMENDED FOCUS (high-energy morning)
   1. Close PR #847 (energy: high, 45 min)
   2. Reply to VP email (10 min)
   3. Prep API review materials (30 min)

3 items in GTD inbox need clarifying
```

### Acceptance Criteria

- Briefing completes in <60 seconds (SC-001)
- Surfaces attention items from all available skills
- Provides actionable recommendations, not just status
- Gracefully handles missing skills (shows what's available)

---

## Story B: Post-Meeting Processing

> **"Layton, process my 1:1 with Sarah"**

### Orchestration Flow

1. **meeting-notes** → `show sarah-1on1-2026-01-13` → Gets transcript + summary
2. **Extract action items** from Gemini summary:
   - "Follow up on API spec by Wednesday"
   - "Schedule meeting with Platform team"
3. **Route to GTD** → `gtd capture "Follow up on API spec" --project "API Redesign"`
4. **Route to Calendar** → "Should I find time for Platform team meeting?"
5. **Update Jira** (if mentioned) → Links conversation to JIRA-1234

### Synthesized Output

```
Processed 1:1 with Sarah (45 min, Gemini summary available)

Captured 2 action items:
  - "Follow up on API spec by Wednesday" -> GTD (project: API Redesign)
  - "Schedule Platform team meeting" -> GTD (waiting: find time)

Related context found:
  - JIRA-1234 mentions API spec (linked)
  - 3 emails from Sarah this week (2 unread)

Shall I draft the API spec response now?
```

### Acceptance Criteria

- Extracts action items from meeting transcripts automatically
- Routes captures to appropriate skill (GTD for tasks, Calendar for scheduling)
- Correlates meeting content with existing entities (Jira tickets, projects)
- Asks before taking write actions (per FR-012)

---

## Story C: Context-Aware "What's Next?"

> **"Layton, what's next?"** (at 3:47 PM, after 90-min API review meeting)

### Context Layton Considers

- **Time**: Late afternoon, likely lower energy
- **Calendar**: No more meetings today
- **Just finished**: 90-min deep meeting (cognitive drain)
- **GTD active list**: 5 tasks at various energy levels

### Synthesized Output

```
3:47 PM - Good time for lighter work before EOD

Given you just finished a 90-min deep session:

LOW-ENERGY OPTIONS (30 min each):
  1. Process GTD inbox (3 items, quick clarification)
  2. Reply to 2 Slack DMs from teammates
  3. Review tomorrow's calendar + prep notes

OR if you have steam left:
  4. Start draft for SRE proposal (high-energy, 45 min)

What feels right?
```

### Acceptance Criteria

- Considers energy level based on time and recent activity
- Presents options ranked by appropriateness to context
- 90% of suggestions are actionable without follow-up (SC-003)
- Respects user agency by offering choices, not mandating

---

## Story D: Weekly Review Synthesis

> **"Layton, let's do weekly review"**

### Cross-Skill Aggregation

```
WEEKLY REVIEW - Jan 6-13, 2026

COMPLETED
  - 12 GTD tasks closed
  - 4 Jira tickets resolved (JIRA-1234, 1238, 1241, 1245)
  - 8 meetings attended (transcripts synced)

STALLED (no activity >5 days)
  - Project "API Redesign" - last action Jan 8
  - JIRA-1198 - blocked, no update since Jan 6

INBOX STATUS
  - GTD: 7 items unclarified
  - Email: 23 flagged, 12 unread
  - Slack: 3 saved messages to process

GOALS PROGRESS (from HORIZONS.md)
  - Q1 Goal: "Ship Sidekick MVP" - 3/7 milestones complete
  - Yearly Goal: "Senior Principal promotion" - on track

COMMITMENTS SLIPPED
  - Promised Sarah API feedback by Jan 10 (missed)
  - Promised Kim SRE proposal by Jan 12 (missed)

NEXT WEEK PREPARATION
  - 5 meetings scheduled (12 hours)
  - 2 deadlines: Jan 17 (API spec), Jan 20 (budget)
```

### Acceptance Criteria

- Surfaces stalled projects and slipped commitments (SC-006)
- Aggregates completion metrics across all skills
- Connects to HORIZONS.md for goal progress
- Identifies upcoming risks (blocked items, heavy meeting load)

---

## Story E: Cross-System Intelligence

> **"Layton, what's happening with the API redesign?"**

### Entity Correlation Across Systems

| System | Query | Findings |
|--------|-------|----------|
| GTD | `gtd list --project "API Redesign"` | 4 open actions, 2 waiting |
| Jira | Issues mentioning "API" | JIRA-1234, 1289 (both open) |
| meeting-notes | Meetings tagged "api" | 3 meetings this month |
| Google Docs (future) | Docs with "API" in title | API Spec Draft v2.1 (3 comments unread) |
| Email (future) | Threads about API | 5 threads, 2 awaiting response |

### Synthesized Output

```
API REDESIGN PROJECT STATUS

GTD ACTIONS
  Active: "Finalize endpoint schema", "Review Sarah's feedback"
  Waiting: "Platform team sign-off", "Security review"

JIRA
  JIRA-1234: API rate limiting (blocked 3 days)
  JIRA-1289: Authentication refactor (in-progress)

RECENT MEETINGS
  Jan 10: API Review with Platform team
    -> Action: "Clarify caching strategy" (uncaptured!)
  Jan 8: 1:1 with Sarah
    -> Discussed timeline concerns

DOCUMENTS
  "API Spec v2.1" - 3 unread comments from Kim

RISKS DETECTED
  - JIRA-1234 blocked - may delay milestone
  - Sarah mentioned concerns about timeline (Jan 8 1:1)
  - You haven't responded to Kim's doc comments (5 days)
```

### Acceptance Criteria

- Semantic entity matching: "API" correlates across systems (SC-004)
- Surfaces uncaptured action items from meeting transcripts
- Detects risks from cross-system patterns
- No explicit entity mappings required (AI-driven correlation)

---

## Story F: Smart Capture Routing

> **"Layton, capture: need to follow up with Kim about the budget spreadsheet she shared in Slack"**

### Parse and Route

```
CAPTURED -> GTD

Title: "Follow up with Kim about budget spreadsheet"
Context: async (Slack-related)
Energy: low (quick follow-up)
Status: active

LINKED CONTEXT (auto-detected):
  - Person: Kim (found in contacts)
  - Document: Budget spreadsheet (searching Google Docs...)
  - Channel: Likely #finance or DM with Kim

Should I:
  1. Add to project "Q1 Budget Planning"?
  2. Set a reminder for tomorrow?
  3. Draft a Slack message to Kim now?
```

### Acceptance Criteria

- Captures route to appropriate skill (GTD for tasks)
- Extracts context labels automatically (async, low energy)
- Correlates mentioned entities (people, documents)
- Offers helpful follow-up actions without auto-executing

---

## Story H: Track This For Me (Attention References)

> **User**: "Keep an eye on JIRA-1234, it's blocking the release"

### The Secretary's Notepad Model

Layton creates an **Attention Reference** - a note that points to something in an external system, NOT a cached copy.

**What Layton stores (in Beads):**

```json
{
  "type": "layton:attention",
  "reference": { "system": "jira", "id": "JIRA-1234" },
  "context": "Blocking release - user asked to track",
  "status": "tracking"
}
```

**What Layton does NOT store:**

- Ticket title, description, status (that's in Jira)
- Assignee, labels, comments (that's in Jira)
- Full ticket history (that's in Jira)

### Flow: Creating an Attention Reference

**User**: "Track JIRA-1234 for me - it's blocking the release and I promised Kim I'd check Monday"

**Layton responds:**

```
Got it! I'll track JIRA-1234 for you.

Created attention reference:
  System: Jira
  Item: JIRA-1234
  Context: "Blocking release - promised Kim to check Monday"
  Reminder: Monday 9:00 AM

I'll surface this in your briefings until it's resolved.
```

### Flow: Attention Reference in Morning Briefing

**Next morning, Layton queries:**

1. **Jira skill** → Gets current JIRA-1234 data (live)
2. **Beads** → Finds attention reference for JIRA-1234

**Layton synthesizes:**

```
ATTENTION ITEMS

📌 JIRA-1234 (you're tracking this)
   Current: Still blocked on QA (3 days now)
   Your note: "Blocking release - promised Kim to check Monday"
   ⏰ Reminder: Check today

   → This hasn't moved since Friday. Should I draft a follow-up to QA?
```

### Flow: Resolving an Attention Reference

**User**: "JIRA-1234 is done, stop tracking it"

**Layton responds:**

```
Marked JIRA-1234 as resolved.

Tracking summary:
  Tracked for: 5 days
  Outcome: Resolved

(Archived to history - won't appear in briefings)
```

### Types of Things to Track

| Source | Example | Reference Stored |
|--------|---------|------------------|
| Jira | "Track JIRA-1234" | `{system: "jira", id: "JIRA-1234"}` |
| Email | "Track that email from VP" | `{system: "email", id: "msg-abc123"}` |
| Slack | "Watch the #incidents thread" | `{system: "slack", id: "thread-xyz"}` |
| PR | "Keep an eye on PR #847" | `{system: "github", id: "PR-847"}` |
| Doc | "Track Kim's budget doc" | `{system: "gdocs", id: "doc-xyz"}` |

### Meta-State: "Since Last Check"

Layton also tracks when each skill was last queried:

```
Morning briefing:
  "3 new emails since you last checked (2 hours ago)"
  "JIRA-1234 was updated since yesterday - moved to In Review"
```

This combines:

- Skill-level timestamp: "Last checked email: 2 hours ago"
- Item-level reference: "You're tracking JIRA-1234"
- Live data: Current state from source system

### Acceptance Criteria

- User can create attention references conversationally (FR-023)
- References store pointers + annotations, not cached data (FR-024)
- Briefings combine references with live skill queries (FR-025)
- Meta-state tracks skill-level and item-level timestamps (FR-026)
- Users can resolve/archive references (FR-027)

---

## Story G: Learning and Adapting Preferences

> **User**: "Actually, always highlight messages from the Platform team too - they're working on the API I depend on"

### Conversational Preference Update

**Layton responds:**

```
Got it! I'll add the Platform team to your tracked people.

This will add to your preferences.md:
  ## People I Track
  + Platform team - monitor for API-related updates

Should I update your preferences file?
```

**User**: "Yes"

**Layton updates `.layton/preferences.md`:**

```markdown
## People I Track
- Sarah Chen (skip-level) - always surface her messages
- Kim (budget owner) - flag any docs awaiting my response
- Platform team - monitor for API-related updates   # <-- Added
```

### Types of Learnable Preferences

| User Says | Layton Adds to preferences.md |
|-----------|-------------------------------|
| "Only show me starred emails" | `## Email Handling` → "Only surface starred messages" |
| "I'm more productive in the morning" | `## Morning Routine` → "Bias toward high-energy tasks before noon" |
| "Ignore the #random channel" | `## Slack` → "Ignore #random channel" |
| "Kim is my budget contact" | `## People I Track` → "Kim (budget owner)" |
| "Jira tickets blocked >3 days are urgent" | `## Jira Priorities` → "Blocked >3 days = urgent" |

### The Two-File Model

```
.layton/
├── config.json        # Structured settings (work hours, timezone, verbosity)
└── preferences.md     # Behavioral instructions (prose, AI-interpreted)
```

| Goes in config.json | Goes in preferences.md |
|--------------------|------------------------|
| `"work_schedule": {"start": "09:00"}` | "Bias toward high-energy before noon" |
| `"timezone": "America/Los_Angeles"` | "Always mention Sarah's messages" |
| `"verbosity": "terse"` | "Lead with calendar in briefings" |
| `"teaching_mode": false` | "Ignore newsletters unless weekly review" |

### Acceptance Criteria

- User can update preferences conversationally (FR-022)
- Layton shows proposed change before writing (explicit confirmation)
- Preferences are prose, not JSON (FR-020)
- Per-skill customization supported (FR-021)
- Changes persist across sessions (stored in `.layton/preferences.md`)

### Example: Building Preferences Over Time

**Week 1:**

```markdown
# My Layton Preferences

## Email Handling
- Only surface starred messages
```

**Week 3 (after several conversations):**

```markdown
# My Layton Preferences

## Email Handling
- Only surface starred messages
- Always highlight VP-level senders
- Ignore newsletters unless weekly review

## Morning Routine
- Lead with calendar first
- Bias toward high-energy tasks before noon
- After 3pm, suggest lighter work

## People I Track
- Sarah Chen (skip-level) - always surface her messages
- Kim (budget owner) - flag docs awaiting response
- Platform team - monitor for API updates

## Jira Priorities
- Focus on release-blocking tickets
- Blocked >3 days = urgent
```

---

## Skill Dependency Map

Layton orchestrates existing skills with future skills adding capability layers:

```
                    +-------------------------------------------+
                    |              LAYTON                       |
                    |        (Orchestrator Skill)               |
                    +---------------------+---------------------+
                                          |
        +---------------------------------+--------------------------------+
        |                                 |                                |
   EXISTING SKILLS                  FUTURE SKILLS                   EXTERNAL MCPs
        |                                 |                                |
   +----+----+                       +----+----+                      +----+----+
   |   GTD   |                       |  Email  |                      | Calendar|
   |  Jira   |                       |  Slack  |                      |   MCP   |
   | meeting-|                       | Google  |                      |         |
   |  notes  |                       |  Docs   |                      |         |
   |  PARA   |                       |         |                      |         |
   +---------+                       +---------+                      +---------+
```

### Progressive Value

| Configuration | Value Delivered |
|--------------|-----------------|
| **Layton only** | Notepad mode - captures, reminders, basic context |
| **+ GTD** | Task management, daily/weekly reviews |
| **+ meeting-notes** | Action item extraction, meeting context |
| **+ Jira** | Work ticket integration, blocker detection |
| **+ Calendar MCP** | Time-aware suggestions, scheduling |
| **+ Email/Slack** (future) | Communication triage, cross-channel awareness |
| **+ Google Docs** (future) | Document activity, comment tracking |

---

## Relationship to Spec User Stories

These concrete scenarios map to the high-level stories in [spec.md](spec.md):

| Spec Story | Concrete Scenarios |
|------------|-------------------|
| **P1: Morning Briefing** | Story A, Story H (attention in briefings) |
| **P2: Adaptive Focus Management** | Story C |
| **P2: Cross-System Intelligence** | Story E, Story H (cross-system tracking) |
| **P3: Weekly/Monthly Planning** | Story D |
| **P3: Skill Delegation with Context** | Story B, Story F |
| **Personalization (FR-020-022)** | Story G |
| **Attention Tracking (FR-023-027)** | Story H |
