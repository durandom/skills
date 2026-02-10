---
name: b4brain
description: Orchestrates GTD and PARA integration. Use for cross-methodology workflows like syncing projects, understanding how the two systems work together, or troubleshooting cross-system issues. For methodology-specific questions, use the standalone gtd or para skills.
---

<essential_principles>

## The Two Layers of b4brain

This system integrates two standalone methodologies:

| Layer | System | Skill | Question It Answers |
|-------|--------|-------|---------------------|
| **Organization** | PARA | `para` skill | "Where does this belong?" |
| **Execution** | GTD | `gtd` skill | "What do I do next?" |

**This skill handles the integration between them.**

### When to Use Each Skill

- **PARA skill** → Folder organization, categorization decisions, archiving
- **GTD skill** → Task capture, clarification, reviews, project milestones
- **b4brain skill** → Syncing projects between PARA and GTD, cross-system decisions, troubleshooting integration issues

### Key Integration Points

1. **GTD H2 (Areas of Focus) ↔ PARA Areas** - Ongoing responsibilities map to `2 Areas/` folder
2. **GTD Projects ↔ PARA Projects** - Milestones (GTD) sync with folders (`1 Projects/`)
3. **GTD Reviews ↔ PARA Review** - Reviews touch both systems

</essential_principles>

<intake>
What would you like to do?

1. **Sync** - Sync PARA projects with GTD milestones
2. **Decide** - Help choosing between GTD and PARA for a task
3. **Troubleshoot** - Cross-system issues
4. **Understand** - How GTD and PARA work together

**Wait for response before proceeding.**
</intake>

<routing>

| Response | Workflow |
|----------|----------|
| 1, "sync", "projects", "milestones" | `workflows/sync-para-gtd.md` |
| 2, "decide", "which", "where", "categorize" | `workflows/guide-decision.md` |
| 3, "troubleshoot", "problem", "stuck", "not working" | `workflows/troubleshoot-system.md` |
| 4, "understand", "explain", "how", "integration" | `workflows/answer-question.md` |
| Other | Clarify intent, then select appropriate workflow |

**After reading the workflow, follow it exactly.**
</routing>

<folder_structure>

## b4brain Folder Structure

The combined PARA + GTD structure:

```
inbox/                 # GTD capture point
├── SCRATCH.md        # Primary quick capture file
└── [captured items]  # Items awaiting processing

1_Projects/           # Active work with deadlines
├── _INDEX.md         # Project overview
└── [Project-Name]/   # One folder per project (synced with GTD milestones)

2_Areas/              # Ongoing responsibilities
├── _INDEX.md         # Area overview
└── [area-name].md    # One file per area

3_Resources/          # Reference material & documentation
├── _INDEX.md         # Resource overview
└── [topic]/          # Topic-based resources

4_Archive/            # Inactive items
├── _INDEX.md         # Archive overview
└── [archived items]  # Completed/inactive content

_GTD_TASKS.md         # Central task list by context (GTD)
```

For folder management, use the `para` skill CLI.
For task management, use the `gtd` skill CLI.

</folder_structure>

<reference_index>

## Domain Knowledge

All in `references/`:

**Integration:**

- unified-workflow.md - How PARA and GTD work together
- b4brain-structure.md - Specific folder conventions and metadata

**Guidance:**

- common-mistakes.md - System-level anti-patterns and recovery strategies
- documentation-patterns.md - Reusable patterns (Watch List, Decision Matrix, Status Badges)

**Optional:**

- zettelkasten-principles.md - Knowledge synthesis method (for reference only)

</reference_index>

<workflows_index>

## Workflows

All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| sync-para-gtd.md | Sync PARA project folders with GTD milestones |
| guide-decision.md | Help choose between GTD and PARA for a task |
| troubleshoot-system.md | Diagnose and fix cross-system problems |
| answer-question.md | Explain integration concepts |

</workflows_index>
