# GTD Clarify Decision Tree

<overview>
This decision tree helps you process items during GTD clarification.
</overview>

<gtd_actionable>

## Is This Actionable?

```
Examine the inbox item
           │
           ▼
Does this require action from me?
├── NO ──┬── Is it trash? ──────────── YES → Delete
│        ├── Is it reference? ─────── YES → File in Resources
│        └── Might I want to later? ── YES → Someday/Maybe list
│
└── YES ──▼

Will it take more than one step?
├── YES → It's a PROJECT
│         1. Define successful outcome
│         2. Create project (milestone)
│         3. Add first next action
│
└── NO ──▼ (Single action)

Can I do it in 2 minutes or less?
├── YES → Do it NOW (don't track)
│
└── NO ──▼

Should someone else do this?
├── YES → Delegate
│         Add to @waiting context
│         Note: "Waiting for: [Person] - [What]"
│
└── NO → Add to task list
         • Choose context
         • Set priority
         • Add due date if time-sensitive
```

</gtd_actionable>

<context_assignment>

## What Context Should This Task Have?

```
Where/how will this task be done?
           │
           ▼
Does it require a computer/laptop?
├── YES → @computer / focus
│         • Coding, email, docs, research
│         • Most knowledge work
│
└── NO ──▼

Does it involve phone/video calls?
├── YES → @calls / meetings
│         • Scheduled calls
│         • Follow-up conversations
│
└── NO ──▼

Must you be physically at a specific location?
├── YES → @office / offsite
│         • Physical documents
│         • In-person meetings
│         • Equipment/resources there
│
└── NO ──▼

Are you waiting for someone else?
├── YES → @waiting (status: waiting)
│         • Delegated tasks
│         • Waiting for response
│
└── NO → @async / @anywhere
         • Can be done asynchronously
         • Not location-dependent
```

</context_assignment>

<priority_assignment>

## What Priority Should This Be?

The GTD CLI uses energy labels (high/low) rather than traditional priority:

```
Evaluate the task
           │
           ▼
Does this require deep focus and mental energy?
├── YES → energy/high
│         • Complex analysis
│         • Creative work
│         • Important decisions
│         • Best for morning/peak hours
│
└── NO ──▼

Is this routine or administrative work?
├── YES → energy/low
│         • Emails, messages
│         • Simple updates
│         • Data entry
│         • Good for low-energy times
│
└── NO → Evaluate based on deadline/impact
```

</priority_assignment>

<review_type>

## Which Review Should I Do?

```
When did you last review?
           │
           ▼
Has it been more than a day since daily review?
├── YES → gtd daily (5 min)
│         • Check priorities
│         • Filter by context
│         • Quick inbox count
│
└── NO ──▼

Has it been more than a week since weekly review?
├── YES → gtd weekly (15 min)
│         • Empty your head
│         • Process inbox to zero
│         • Check all projects have next actions
│         • Review someday/maybe
│
└── NO ──▼

Has it been more than a quarter since quarterly review?
├── YES → gtd quarterly (1 hr)
│         • Review goals
│         • Check project progress
│         • Adjust horizons
│
└── NO ──▼

Has it been more than a year since yearly review?
├── YES → gtd yearly (2 hr)
│         • Review vision and purpose
│         • Set yearly goals
│         • Strategic planning
│
└── NO → No review needed right now
         Focus on doing the work
```

</review_type>
