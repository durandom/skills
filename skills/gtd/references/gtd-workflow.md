<overview>
The GTD (Getting Things Done) methodology by David Allen provides a systematic approach to managing tasks and commitments. This system implements GTD's core principles with a Python CLI backed by GitHub Issues.
</overview>

<five_steps>

## The 5 GTD Steps

### 1. Capture

Get everything out of your head into the system. Don't evaluate, just capture.

```bash
./gtd capture "Call John about project timeline"
./gtd capture "Research new plugin framework"
./gtd capture "Prepare slides for Monday standup"
```

Items go to the inbox (status/someday with no other labels).

### 2. Clarify

Process each inbox item with the clarification questions:

```bash
./gtd inbox      # See what needs clarifying
./gtd clarify 42 # Process item #42
```

**Clarification questions:**

1. Is it actionable?
   - **No** → Delete, Someday/Maybe, or Reference
   - **Yes** → Continue to next question
2. What's the successful outcome?
3. What's the very next physical action?

### 3. Organize

Assign labels during clarification:

- **Context**: Where/when can this be done? (focus, meetings, async, offsite)
- **Energy**: How much mental effort? (high, low)
- **Status**: Workflow state (active, waiting, someday)
- **Horizon**: What level? (action, project, goal)

### 4. Reflect

Regular reviews keep the system trusted:

**Daily (5 min):**

```bash
./gtd daily
```

- Review today's work by context/energy
- Check blocked/waiting items
- Quick inbox check

**Weekly (15-30 min):**

```bash
./gtd weekly
```

- Process inbox to zero
- Review active items
- Check waiting items
- Review projects (ensure each has a next action)
- Review someday/maybe

### 5. Engage

Work from filtered lists, not the full backlog:

```bash
# Morning focus block
./gtd list --context focus --energy high --status active

# Between meetings
./gtd list --energy low --status active

# Afternoon async work
./gtd list --context async --status active
```

</five_steps>

<inbox_workflow>

## Inbox Processing Workflow

When you run `gtd clarify <id>`, follow this decision tree:

```
Is it actionable?
├── NO
│   ├── Trash → Close the issue
│   ├── Someday/Maybe → Keep status/someday
│   └── Reference → Move to notes system
│
└── YES
    ├── What's the outcome? (Document it)
    ├── What's the next action? (Make it the title)
    │
    └── Can it be done in 2 minutes?
        ├── YES → Do it now, then close
        └── NO → Organize with labels (status/active, horizon/action)
```

</inbox_workflow>

<two_minute_rule>

## The Two-Minute Rule

If the next action takes less than 2 minutes, do it immediately.

- Don't bother labeling
- Don't track it
- Just do it and close

This prevents the system from filling with trivial items.
</two_minute_rule>

<next_actions>

## Good vs Bad Next Actions

**Bad next actions (vague):**

- "Handle the budget"
- "Do something about the plugin"
- "Figure out the API"

**Good next actions (physical, specific):**

- "Email Susan to request Q4 budget spreadsheet"
- "Open plugin repo and review open PRs"
- "Read API docs section on authentication"

A next action should be:

- Physical (can be done without thinking)
- Specific (clear what "done" looks like)
- Immediate (no preceding steps required)
</next_actions>

<contexts>

## Context-Based Work

Don't look at your full task list. Filter by context:

**Focus context (morning, 8am-1pm):**

- Deep work requiring concentration
- Architecture, design, writing
- No interruptions expected

**Meetings context (afternoon, 2-6pm):**

- Synchronous collaboration
- Calls, live discussions
- Prepared talking points

**Async context (anytime):**

- Slack threads, email, comments
- Google Docs reviews
- Issue tracker updates

**Offsite context (travel days):**

- Customer visits
- Team offsites
- Travel prep
</contexts>

<reviews>

## Review Rhythms

**Daily review (5 min):**

- `./gtd daily`
- Scan today's work
- Note any blockers
- Quick inbox check

**Weekly review (15-30 min):**

- `./gtd weekly`
- Process inbox to zero
- Review active items
- Check waiting items
- Review projects

**Quarterly review (1-2 hours):**

- `./gtd quarterly`
- Review goals (horizon/goal)
- Review project progress
- Update Areas of Focus
- Set next quarter focus

**Yearly review (2-4 hours):**

- `./gtd yearly`
- Review vision and purpose
- Set yearly goals
- Reflect on achievements
</reviews>

<anti_patterns>

## Common GTD Mistakes

### Mistake: Capturing without clarifying

- Inbox grows forever
- Items become stale
- System loses trust

**Fix:** Process inbox daily or weekly to zero.

### Mistake: Vague next actions

- "Handle project" sits for weeks
- Procrastination builds

**Fix:** Make next actions physical and specific.

### Mistake: Looking at full list

- Overwhelm and paralysis
- Context switching

**Fix:** Always filter by context/energy/status.

### Mistake: Skipping reviews

- System becomes outdated
- Trust erodes

**Fix:** Protect review time. Daily = 5 min, Weekly = 15 min.
</anti_patterns>
