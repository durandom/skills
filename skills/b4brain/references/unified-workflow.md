# Unified Workflow Reference

<overview>
The b4brain system integrates GTD and PARA into a simple two-layer system optimized for **capture, organization, and retrieval**. The goal is a reliable second brain - fast to capture, easy to find.
</overview>

<two_layers>

## The Two-Layer Model

| Layer | Methodology | Purpose | Question Answered |
|-------|-------------|---------|-------------------|
| **Execution** | GTD | Capture and process everything | "What do I do next?" |
| **Organization** | PARA | Structure by actionability | "Where does this belong?" |

**Each layer serves a distinct purpose:**

- **GTD** clears your head by externalizing everything into a trusted system
- **PARA** creates focus by organizing information based on when you'll need it
</two_layers>

<information_flow>

## How Information Flows Through the System

```
                    CAPTURE
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                  GTD LAYER                   │
│                                              │
│  inbox/ ──► /inbox ──► Clarify + Organize   │
│                              │               │
└──────────────────────────────┼───────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
┌──────────────────────────────────────────────┐
│                 PARA LAYER                   │
│                                              │
│  1 Projects/    2 Areas/    3 Resources/    │
│  (active work)  (ongoing)   (reference)     │
│                                              │
│            ──► Searchable & Retrievable     │
└──────────────────────────────────────────────┘
                       │
                       ▼
                 4 Archive/
                 (inactive)
```

**The flow is simple:**

1. Capture everything (GTD inbox)
2. Clarify and organize (GTD processing)
3. File by actionability (PARA categories)
4. Retrieve when needed (search + browse)
5. Archive when done (PARA archive)
</information_flow>

<gtd_para_integration>

## How GTD and PARA Work Together

<interaction name="Capture → Inbox">
**When:** Something happens you need to remember

**Action:** `/capture` immediately

- Don't think about where it goes
- Don't organize yet
- Just get it into SCRATCH.md

**Example:**

```
You configure your NAS with a new share
→ /capture "Set up new media share on NAS, used SMB with guest access"
```

</interaction>

<interaction name="Inbox → PARA">
**When:** Processing captured items with `/inbox`

**Flow:**

1. Is it actionable with a deadline? → `1 Projects/`
2. Is it an ongoing responsibility? → `2 Areas/`
3. Is it reference material for later? → `3 Resources/`
4. Is it trash? → Delete

**Example:**

```
Processing: "Set up new media share on NAS, used SMB with guest access"
Clarify: Not actionable, it's documentation of what I did
Organize: → 3 Resources/nas-configuration/media-shares.md
```

</interaction>

<interaction name="Need → Search → Retrieve">
**When:** You need to find something you documented

**Flow:**

1. Search Obsidian (Cmd/Ctrl + Shift + F)
2. Browse relevant PARA folder
3. Check `_INDEX.md` files

**Example:**

```
Need: "How did I set up that NAS share again?"
Search: "NAS share SMB"
Find: 3 Resources/nas-configuration/media-shares.md
```

</interaction>
</gtd_para_integration>

<daily_workflow>

## Daily Workflow

**Morning:**

1. `/review daily` - Check priorities in `_GTD_TASKS.md`
2. Filter tasks by context (e.g., `@computer`)
3. Work on highest priority items

**During work:**
4. Ideas/interruptions → `/capture` immediately
5. Focus returns to current task
6. Complete tasks, mark done in `_GTD_TASKS.md`
7. **Document significant work** in appropriate Resources folder

**End of day:**
8. Quick `/review daily` to capture loose ends
9. Set tomorrow's priorities

**Weekly:**
10. `/review weekly` - Full system review
11. `/inbox` until inbox is empty
12. Update `_INDEX.md` files if needed
</daily_workflow>

<documentation_habit>

## The Key Habit: Document What You Do

Since this system is optimized for **retrieval**, documentation is crucial.

**When to document:**

- Set up or configure something
- Make a significant decision
- Solve a tricky problem
- Learn something you'll need again

**What to include:**

- **What** you did (steps, commands, settings)
- **Why** you made certain choices
- **Date** for context
- **Links** to related resources

**Template for technical documentation:**

```markdown
# [Thing You Configured]

## Date
YYYY-MM-DD

## What I Did
[Brief description]

## Key Settings/Configuration
[Specifics - commands, settings, values]

## Why These Choices
[Reasoning for decisions made]

## Gotchas/Notes
[Things that weren't obvious]

## Related
- [[other-relevant-note]]
```

</documentation_habit>

<when_to_use_what>

## When to Use Each Command

| Situation | Command | Why |
| --- | --- | --- |
| Quick thought to save | `/capture` | Don't interrupt flow |
| Processing captured items | `/inbox` | Clarify and organize |
| Checking priorities | `/review daily` | See what to do |
| Full system check | `/review weekly` | Maintain the system |
| Creating a project | `/project` | Set up structure |
| Finding something | `/search` or Obsidian search | Retrieve what you need |
| Updating indexes | `/index` | Keep navigation current |

</when_to_use_what>

<integration_benefits>

## Why This Works

**GTD alone:** Good task capture, but:

- Reference material has no home
- No clear organization structure

**PARA alone:** Good organization, but:

- No workflow for processing items
- Unclear how things get into folders

**GTD + PARA together:**

- Clear capture point (inbox)
- Systematic processing (/inbox)
- Organized storage (PARA folders)
- Easy retrieval (search + structure)
- Clean archives (completed/inactive)
</integration_benefits>

<failure_modes>

## Common Failures

### 1. Skipping capture

- Symptom: Things stay in your head, get forgotten
- Fix: `/capture` immediately, always

### 2. Not processing inbox

- Symptom: Inbox overflows, becomes useless
- Fix: Daily quick processing, weekly empty

### 3. Poor documentation

- Symptom: Can't find what you did, re-learn things
- Fix: Document when you do, include the why

### 4. Not using search

- Symptom: Can't find things, think they're lost
- Fix: Obsidian search is powerful, use it

### 5. Skipping reviews

- Symptom: System drifts, loses trust
- Fix: Daily 5-min, weekly 15-min reviews
</failure_modes>
