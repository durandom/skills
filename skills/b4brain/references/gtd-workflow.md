# GTD Workflow Reference

<overview>
Getting Things Done (GTD) by David Allen is a productivity methodology for capturing all commitments externally and processing them systematically. The goal is "mind like water" - a clear head that reacts appropriately to inputs without anxiety from forgotten commitments.
</overview>

<core_principle>

## The Core Innovation: External Trusted System

GTD's insight: Your mind is for having ideas, not holding them.

**The problem:** Open loops (uncaptured commitments) create:

- Background anxiety
- Mental fatigue
- Reactive rather than proactive behavior
- Lost ideas and forgotten tasks

**The solution:** Capture everything into a trusted system, process it systematically, and review regularly. The system holds the commitments; your mind stays clear.
</core_principle>

<five_steps>

## The GTD Workflow (5 Steps)

<step name="1. Capture">
**What:** Get everything out of your head into a collection tool.

**In b4brain:**

- `/capture` adds to `inbox/SCRATCH.md`
- Any thought, idea, task, or commitment
- Don't organize yet - just capture
- Speed > perfection

**Capture triggers:**

- Meeting action items
- Random thoughts
- URLs and articles
- Email commitments
- Ideas during work

**Command:** `/capture "your thought here"`
</step>

<step name="2. Clarify">
**What:** Process each captured item to determine what it is and what to do with it.

**The clarifying questions:**

1. **Is it actionable?**
   - NO → Trash, Reference (Resources), or Someday/Maybe
   - YES → Continue...

2. **What's the successful outcome?**
   - Define what "done" looks like
   - Multi-step = Project
   - Single-step = Task

3. **What's the very next physical action?**
   - Must be concrete and specific
   - "Finalize report" → "Open report.docx and write conclusion paragraph"

**In b4brain:** `/inbox` processes one item through this workflow
</step>

<step name="3. Organize">
**What:** Put clarified items where they belong.

**GTD lists mapped to b4brain:**

| GTD List | b4brain Location | Contents |
|----------|------------------|----------|
| Projects | `1 Projects/` | Multi-step outcomes |
| Next Actions | `_GTD_TASKS.md` | Concrete tasks by context |
| Waiting For | `_GTD_TASKS.md` @waiting | Delegated items |
| Someday/Maybe | `3 Resources/` | Future possibilities |
| Reference | `3 Resources/` | Non-actionable info |

**Context tags in b4brain:**

- `@computer` - Requires computer
- `@calls` - Phone/video communication
- `@office` - Must be at office
- `@home` - Personal/home tasks
- `@anywhere` - Can do anywhere
- `@waiting` - Waiting for someone
- `@review` - Needs deeper thinking

**Priority levels:**

- 🔥 High - Critical/urgent
- ⚠️ Medium - Important but not urgent
- 💡 Low - Nice to have
</step>

<step name="4. Reflect">
**What:** Review the system regularly to maintain trust.

**In b4brain:** `/review` command

**Daily review (5 min):**

- Check today's priorities in `_GTD_TASKS.md`
- Quick inbox count (don't process)
- Identify top 3 priorities for the day

**Weekly review (15 min):**

- Empty your head (capture anything uncaptured)
- Process inbox to zero
- Review all projects for next actions
- Check Someday/Maybe list
- Update priorities

**Monthly review (30 min):**

- Archive completed projects
- Review Areas for health
- Analyze knowledge graph
- Evaluate system effectiveness
</step>

<step name="5. Engage">
**What:** Do the work based on context, time, energy, and priority.

**Decision criteria (in order):**

1. **Context:** What can I do here? (filter by @context)
2. **Time available:** How long do I have?
3. **Energy:** High-focus or routine tasks?
4. **Priority:** 🔥 before ⚠️ before 💡

**The power of context tags:**
When you have 10 minutes between meetings:

- Filter `_GTD_TASKS.md` by `@anywhere`
- Pick task matching available energy
- Make progress without decision fatigue
</step>

</five_steps>

<clarify_decision_tree>

## Clarify Decision Tree

```
INBOX ITEM
    │
    ▼
Is it actionable?
├── NO ──┬── Is it trash? ──── YES → Delete
│        ├── Reference? ────── YES → 3 Resources/
│        └── Someday/Maybe? ── YES → S/M list
│
└── YES ─┬── What's the outcome?
         │
         ├── Multi-step (Project)
         │   └── Create in 1 Projects/
         │       Define next action → _GTD_TASKS.md
         │
         └── Single-step (Task)
             ├── <2 minutes? → Do it now
             ├── Delegate? → @waiting in _GTD_TASKS.md
             └── Defer → _GTD_TASKS.md with context
```

</clarify_decision_tree>

<b4brain_implementation>

## GTD in b4brain

**Capture layer:**

- `inbox/SCRATCH.md` - Primary capture file
- `inbox/` folder - Larger captured items
- `/capture` command for quick input

**Processing:**

- `/inbox` - Process ONE item at a time
- Forces clarification questions
- Extracts tasks with contexts
- Files into PARA structure

**Task management:**

- `_GTD_TASKS.md` - Central task list
- Organized by context (@computer, @calls, etc.)
- Includes project references
- Priority indicators (🔥 ⚠️ 💡)

**Review:**

- `/review daily` - Priorities and inbox check
- `/review weekly` - Full system review
- `/review monthly` - Strategic review
</b4brain_implementation>

<next_action_examples>

## Good vs Bad Next Actions

**Bad (vague):**

- "Work on presentation"
- "Handle email"
- "Fix the bug"

**Good (concrete):**

- "Open slides.pptx and write the introduction slide"
- "Reply to Sarah's email about the meeting time"
- "Reproduce the login bug using test user credentials"

**The test:** Can you visualize yourself doing it? If not, it's not a next action.
</next_action_examples>

<two_minute_rule>

## The Two-Minute Rule

If a task takes less than 2 minutes, do it immediately.

**Why:** The overhead of tracking a 2-minute task exceeds the task itself.

**Application in `/inbox`:** When processing, if next action is <2 min, do it now rather than adding to `_GTD_TASKS.md`.
</two_minute_rule>
