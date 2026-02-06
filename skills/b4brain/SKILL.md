---
name: b4brain
description: Domain expertise on PARA and GTD methodologies as implemented in the b4brain personal knowledge management system. Use when users ask questions about the methodologies, need help with categorization decisions, or want to troubleshoot workflow issues.
---

<essential_principles>

## The Two Layers of b4brain

This system integrates two methodologies for **capture, organization, and retrieval**:

| Layer | System | Purpose | Question It Answers |
|-------|--------|---------|---------------------|
| **Organization** | PARA | Structure by actionability | "Where does this belong?" |
| **Execution** | GTD | Capture, clarify, complete tasks | "What do I do next?" |

**Design goal:** A reliable second brain for fast capture and retrieval - not knowledge synthesis.

### 1. PARA Organizes by Actionability, Not Topic

Information is filed based on **when you'll need it**, not what it's about:

- **Projects** → Active work with deadlines (most actionable)
- **Areas** → Ongoing responsibilities without end dates
- **Resources** → Reference material for future use (documentation, how-tos, configs)
- **Archive** → Inactive items from above categories (least actionable)

A Kubernetes article goes in Projects if you're deploying now, Areas if you maintain Kubernetes systems, or Resources if you're just interested.

### 2. GTD Externalizes Mental Load

The goal is "mind like water" - nothing floating in your head. Everything gets:

1. **Captured** → Into inbox (SCRATCH.md or inbox/)
2. **Clarified** → Is it actionable? What's the outcome? What's the next action?
3. **Organized** → Filed into PARA structure with tasks in _GTD_TASKS.md
4. **Reflected** → Daily/weekly/monthly reviews
5. **Engaged** → Do the work based on context and energy

### 3. Good Documentation Is the Key

Since this is a personal vault optimized for **retrieval**, the most important habit is:

- **Document what you do** when you configure, set up, or decide something
- **Include the "why"** so future-you understands the reasoning
- **Make it searchable** with clear titles and consistent structure

### 4. Commands Execute, This Skill Explains

The `/capture`, `/inbox`, `/review`, `/project` commands **do the work**. This skill **explains the methodology** - when to use each command, why the system works this way, and how to troubleshoot issues.
</essential_principles>

<intake>
**What would you like to know about?**

1. **Understand a methodology** - Learn about PARA or GTD
2. **Make a decision** - Help categorizing something or choosing an approach
3. **Troubleshoot** - Something isn't working or feels off
4. **Compare approaches** - When to use what

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "understand", "explain", "what is", "how does", "learn" | `workflows/answer-question.md` |
| 2, "decide", "categorize", "where should", "which", "should I" | `workflows/guide-decision.md` |
| 3, "troubleshoot", "problem", "not working", "stuck", "overwhelmed", "too many" | `workflows/troubleshoot-system.md` |
| 4, "compare", "difference", "vs", "versus", "when to use" | `workflows/answer-question.md` |
| Other | Clarify intent, then select appropriate workflow |

**After reading the workflow, follow it exactly.**
</routing>

<command_reference>

## b4brain Commands Quick Reference

| Command | Purpose | When to Use |
| --- | --- | --- |
| `/capture` | Quick capture to inbox | Anytime you have a thought, URL, or file to save |
| `/inbox` | GTD clarify + organize | Processing captured items one at a time |
| `/review` | Reflect on system state | Daily (priorities), weekly (projects), monthly (strategy) |
| `/project` | Project lifecycle | Create, track, or archive projects |
| `/search` | Cross-folder search | Find content across PARA structure |
| `/index` | Maintain indexes | Update PARA folder _INDEX.md files |
| `/defrag` | System maintenance | Clean up and reorganize structure |

</command_reference>

<folder_structure>

## PARA Folder Structure

```
inbox/                 # GTD capture point
├── SCRATCH.md        # Primary quick capture file
└── [captured items]  # Items awaiting processing

1_Projects/           # Active work with deadlines
├── _INDEX.md         # Project overview
└── [Project-Name]/   # One folder per project

2_Areas/              # Ongoing responsibilities
├── _INDEX.md         # Area overview
└── [area-name].md    # One file per area (or folder if complex)

3_Resources/          # Reference material & documentation
├── _INDEX.md         # Resource overview
└── [topic]/          # Topic-based resources (configs, how-tos, references)

4_Archive/            # Inactive items
├── _INDEX.md         # Archive overview
└── [archived items]  # Completed/inactive content

_GTD_TASKS.md         # Central task list by context
```

</folder_structure>

<reference_index>

## Domain Knowledge

All in `references/`:

**Core Methodologies:**

- para-method.md - PARA principles and application
- gtd-workflow.md - GTD capture-clarify-organize-reflect-engage

**Integration:**

- unified-workflow.md - How PARA and GTD work together
- b4brain-structure.md - Specific folder conventions and metadata

**Guidance:**

- decision-trees.md - When to use which approach
- common-mistakes.md - Anti-patterns and troubleshooting
- documentation-patterns.md - Reusable patterns (Watch List, Decision Matrix, Status Badges)

**Optional (not part of core system):**

- zettelkasten-principles.md - Knowledge synthesis method (for reference only)
</reference_index>

<workflows_index>

## Workflows

All in `workflows/`:

| Workflow | Purpose |
| --- | --- |
| answer-question.md | Explain methodology concepts |
| guide-decision.md | Help with categorization and approach decisions |
| troubleshoot-system.md | Diagnose and fix workflow problems |

</workflows_index>
