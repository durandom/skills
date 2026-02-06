# Decision Trees Reference

<overview>
This reference provides decision trees and guidance for common choices in the b4brain system. Use these when uncertain about categorization, commands, or workflow.
</overview>

<para_categorization>

## Where Does This Belong? (PARA Decision)

```
Start with the item to organize
           │
           ▼
Is there active work on this with a deadline?
├── YES → 1_Projects/
│         • Has clear outcome
│         • Has timeline
│         • Can be "completed"
│
└── NO ──▼

Is this an ongoing responsibility I maintain?
├── YES → 2_Areas/
│         • No end date
│         • Has standards to maintain
│         • Part of a role/responsibility
│
└── NO ──▼

Could this be useful reference material later?
├── YES → 3_Resources/
│         • Topic of interest
│         • No immediate use
│         • Reference value
│
└── NO ──▼

Is this completed/historical but worth keeping?
├── YES → 4_Archive/
│         • Completed project
│         • Past reference
│         • Historical record
│
└── NO → Delete it
```

</para_categorization>

<gtd_actionable>

## Is This Actionable? (GTD Clarify)

```
Examine the inbox item
           │
           ▼
Does this require action from me?
├── NO ──┬── Is it trash? ──────────── YES → Delete
│        ├── Is it reference? ─────── YES → 3_Resources/
│        └── Might I want to later? ── YES → Someday/Maybe list
│
└── YES ──▼

Will it take more than one step?
├── YES → It's a PROJECT
│         1. Create in 1_Projects/
│         2. Define successful outcome
│         3. Add tasks to _GTD_TASKS.md
│
└── NO ──▼ (Single action)

Can I do it in 2 minutes or less?
├── YES → Do it NOW (don't track)
│
└── NO ──▼

Should someone else do this?
├── YES → Delegate
│         Add to @waiting in _GTD_TASKS.md
│         Note: "Waiting for: [Person] - [What]"
│
└── NO → Add to _GTD_TASKS.md
         • Choose context (@computer, @calls, etc.)
         • Set priority (🔥 ⚠️ 💡)
         • Add due date if time-sensitive
```

</gtd_actionable>

<which_command>

## Which Command Should I Use?

```
What are you trying to do?
           │
           ▼
Quickly save a thought/URL/file?
├── YES → /capture
│
└── NO ──▼

Process items in inbox?
├── YES → /inbox
│         (Process ONE item at a time)
│
└── NO ──▼

Check priorities or system health?
├── YES → /review
│         • /review daily - priorities
│         • /review weekly - full review
│         • /review monthly - strategic
│
└── NO ──▼

Create, track, or archive a project?
├── YES → /project
│         • /project "Name" - create
│         • /project status - view all
│         • /project complete "Name" - archive
│
└── NO ──▼

Find content across the system?
├── YES → /search or Obsidian search (Cmd/Ctrl+Shift+F)
│
└── NO ──▼

Maintain index files?
├── YES → /index
│
└── NO → Maybe you don't need a command
          (Just work directly in the vault)
```

</which_command>

<context_assignment>

## What Context Should This Task Have?

```
Where/how will this task be done?
           │
           ▼
Does it require a computer/laptop?
├── YES → @computer
│         • Coding, email, docs, research
│         • Most knowledge work
│
└── NO ──▼

Does it involve phone/video calls?
├── YES → @calls
│         • Scheduled calls
│         • Follow-up conversations
│         • Voice communication
│
└── NO ──▼

Must you be physically at the office?
├── YES → @office
│         • Physical documents
│         • In-person meetings
│         • Equipment/resources there
│
└── NO ──▼

Must you be at home?
├── YES → @home
│         • Personal tasks
│         • Home maintenance
│         • Requires home resources
│
└── NO ──▼

Are you waiting for someone else?
├── YES → @waiting
│         • Delegated tasks
│         • Waiting for response
│         • Blocked by others
│
└── NO ──▼

Does it need thinking time (not action)?
├── YES → @review
│         • Deep thinking required
│         • Planning/designing
│         • Complex decisions
│
└── NO → @anywhere
         • Reading
         • Simple tasks
         • Can do in any location
```

</context_assignment>

<priority_assignment>

## What Priority Should This Be?

```
Evaluate the task
           │
           ▼
Is there a hard deadline or urgent need?
├── YES → Does missing it cause significant harm?
│         ├── YES → 🔥 High
│         │         • Critical deadlines
│         │         • Production issues
│         │         • Blocking others
│         │
│         └── NO → ⚠️ Medium
│                   • Important but flexible
│                   • Soft deadlines
│                   • Should do this week
│
└── NO ──▼

Is this important for goals or responsibilities?
├── YES → ⚠️ Medium
│         • Important but not urgent
│         • Contributes to long-term goals
│         • Part of area responsibility
│
└── NO → 💡 Low
         • Nice to have
         • No deadline
         • Optional improvement
```

</priority_assignment>

<review_type>

## Which Review Should I Do?

```
When did you last review?
           │
           ▼
Has it been more than a day since daily review?
├── YES → /review daily (5 min)
│         • Check priorities
│         • Filter by context
│         • Quick inbox count
│
└── NO ──▼

Has it been more than a week since weekly review?
├── YES → /review weekly (15 min)
│         • Empty your head
│         • Process inbox to zero
│         • Check all projects have next actions
│         • Review someday/maybe
│
└── NO ──▼

Has it been more than a month since monthly review?
├── YES → /review monthly (30 min)
│         • Archive completed work
│         • Review area health
│         • Evaluate system effectiveness
│
└── NO → No review needed right now
         Focus on doing the work
```

</review_type>
