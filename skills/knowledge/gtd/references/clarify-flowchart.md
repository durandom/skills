# GTD Clarify Flowchart

The classic David Allen "What do I do with this?" decision tree.

```
                              ┌─────────┐
                              │  STUFF  │
                              │ (inbox) │
                              └────┬────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │  What is it?   │
                          └───────┬────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Is it actionable? │
                       └──────────┬──────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼ NO                              ▼ YES
    ┌────────────────────────┐          ┌─────────────────────┐
    │   What kind of thing   │          │ What's the desired  │
    │       is it?           │          │      outcome?       │
    └────────────┬───────────┘          └──────────┬──────────┘
                 │                                 │
       ┌─────────┼─────────┐                       │
       │         │         │                       ▼
       ▼         ▼         ▼              ┌────────────────────┐
   ┌───────┐ ┌───────┐ ┌─────────┐        │  Is it a project   │
   │ TRASH │ │SOMEDAY│ │REFERENCE│        │ (multi-step)?      │
   │       │ │ MAYBE │ │         │        └─────────┬──────────┘
   │delete │ │       │ │ vault   │                  │
   └───────┘ │status/│ │ or note │         ┌───────┴───────┐
             │someday│ └─────────┘         │               │
             └───────┘                     ▼ YES           ▼ NO
                                  ┌──────────────┐  ┌──────────────┐
                                  │   PROJECT    │  │    ACTION    │
                                  │              │  │              │
                                  │horizon/      │  │horizon/      │
                                  │project       │  │action        │
                                  └──────┬───────┘  └──────┬───────┘
                                         │                 │
                                         │                 │
                                         └────────┬────────┘
                                                  │
                                                  ▼
                                    ┌──────────────────────┐
                                    │ What's the NEXT      │
                                    │ physical action?     │
                                    └───────────┬──────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          │                     │                     │
                          ▼                     ▼                     ▼
                 ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
                 │   < 2 MINUTES   │   │    DELEGATE     │   │      DEFER      │
                 │                 │   │                 │   │                 │
                 │   DO IT NOW     │   │  status/waiting │   │  status/active  │
                 │                 │   │  + waiting_for  │   │  + context      │
                 │   gtd done <id> │   │                 │   │  + energy       │
                 └─────────────────┘   └─────────────────┘   └────────┬────────┘
                                                                      │
                                                    ┌─────────────────┴─────────────────┐
                                                    │                                   │
                                                    ▼                                   ▼
                                           ┌───────────────┐                   ┌───────────────┐
                                           │ SPECIFIC DATE │                   │ AS SOON AS    │
                                           │               │                   │ POSSIBLE      │
                                           │ Calendar or   │                   │               │
                                           │ gtd defer     │                   │ Next Actions  │
                                           └───────────────┘                   │ list          │
                                                                               └───────────────┘
```

## Decision Summary

| Question | Answer | Action | GTD Command |
|----------|--------|--------|-------------|
| Is it actionable? | No - Trash | Delete | `gtd clarify <id> --not-actionable --delete` |
| Is it actionable? | No - Maybe later | Someday/Maybe | `gtd clarify <id> --not-actionable --someday` |
| Is it actionable? | No - Reference | Store in vault | `gtd clarify <id> --not-actionable --reference` |
| Multi-step outcome? | Yes | Create project | `gtd add "..." --horizon project` |
| Next action < 2 min? | Yes | **Do it now** | `gtd done <id>` |
| Next action - delegate? | Yes | Waiting for | `gtd clarify <id> --status waiting` then `gtd waiting <id> <person>` |
| Next action - specific date? | Yes | Defer | `gtd clarify <id> --status active` then `gtd defer <id> <date>` |
| Next action - ASAP? | Yes | Active | `gtd clarify <id> --status active --context <ctx> --energy <lvl>` |

## The 2-Minute Rule

**Critical:** If the next action takes less than 2 minutes, **do it immediately**. Don't track it.

Why? The overhead of tracking (capture → clarify → organize → review → engage) exceeds the time to just do it.

```bash
# Item in inbox takes 1 minute to do?
# DON'T: gtd clarify 123 --status active --context async --energy low
# DO:    Just do it, then: gtd done 123
```

## Labels Applied at Each Decision Point

```
NOT ACTIONABLE:
  ├── Trash      → (delete, no labels)
  ├── Someday    → status/someday (keep in someday/maybe list)
  └── Reference  → (move to vault, no GTD tracking)

ACTIONABLE:
  ├── Project    → horizon/project
  └── Action     → horizon/action
                      │
                      ├── Delegate  → status/waiting + waiting_for metadata
                      └── Defer     → status/active + context/* + energy/*
                                        │
                                        ├── Specific date → defer_until metadata
                                        └── ASAP → Next Actions list
```

## Context Labels (Where/When)

| Context | When to Use |
|---------|-------------|
| `context/focus` | Deep work, no interruptions (morning) |
| `context/meetings` | Synchronous time, calls, collab |
| `context/async` | Anytime, interruptible (Slack, email) |
| `context/offsite` | Travel, customer visits, offsites |

## Energy Labels (Mental Load)

| Energy | When to Use |
|--------|-------------|
| `energy/high` | Requires concentration, preparation |
| `energy/low` | Quick, routine, low cognitive load |
