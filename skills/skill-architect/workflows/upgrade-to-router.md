# Workflow: Upgrade a Simple Skill to Router Pattern

<required_reading>
Read first:

1. `references/architecture-patterns.md` — router pattern structure
2. `references/writing-philosophy.md` — principles vs procedures
</required_reading>

<process>

## Step 1: Read the Current Skill

```bash
cat {skill-path}/SKILL.md
ls {skill-path}/
```

**Confirm it needs upgrading.** Signs it should stay simple:
- Under 200 lines, single workflow → router pattern is overkill
- Only one thing a user would ever want to do

**Good candidates for upgrade:**
- Over 200 lines
- Multiple distinct user intents ("create? audit? optimize?")
- Principles that must apply across all use cases
- Growing complexity

If it should stay simple, tell the user and offer to add content instead.

## Step 2: Identify the Components

Analyze the current skill and identify:

1. **Essential principles** — rules that apply to ALL use cases, regardless of workflow
2. **Distinct workflows** — different things a user might want to do (these become workflow files)
3. **Reusable knowledge** — patterns, examples, technical details (these become reference files)

Present findings and confirm with user:

```
## Analysis

Essential principles (always apply):
- [Principle 1]
- [Principle 2]

Distinct workflows (user intents):
- [Workflow A]: [description]
- [Workflow B]: [description]

Reusable knowledge (shared across workflows):
- [Topic 1]
- [Topic 2]

Does this breakdown look right?
```

## Step 3: Create Directory Structure

```bash
mkdir -p {skill-path}/workflows
mkdir -p {skill-path}/references
# Add templates/ and scripts/ only if needed
```

## Step 4: Extract Workflows

For each identified user intent:

1. Create `workflows/{intent-name}.md`
2. Add `<required_reading>` listing which references this workflow needs
3. Move the relevant procedure steps into `<process>`
4. Add `<success_criteria>` (verifiable, not "user is satisfied")

## Step 5: Extract References

For each identified knowledge topic:

1. Create `references/{topic-name}.md`
2. Move relevant knowledge from original skill
3. Structure with decision guidance ("if X, use Y; if Z, use A")

## Step 6: Rewrite SKILL.md as Router

Replace the SKILL.md content with the router structure:

```markdown
---
name: {skill-name}
description: {updated description — include all workflows in trigger phrases}
---

<essential_principles>

## [Core concept title]

[Principles extracted in Step 2 — inline here, cannot be skipped]

### 1. [First principle]
[Explanation of *why*, not just what]

### 2. [Second principle]
[Explanation]
</essential_principles>

<intake>
What would you like to do?

1. [Workflow A option]
2. [Workflow B option]
3. [Workflow C option]

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "keywords" | `workflows/workflow-a.md` |
| 2, "keywords" | `workflows/workflow-b.md` |

**Intent-based routing (if user provides clear intent without selecting menu):**
- "create", "build", "new" → workflows/workflow-a.md
- "audit", "check", "review" → workflows/workflow-b.md

**After reading the workflow, follow it exactly.**
</routing>

<reference_index>

## Domain Knowledge

All in `references/`:

**[Category]:** topic-a.md — [one-line purpose]
**[Category]:** topic-b.md — [one-line purpose]
</reference_index>

<workflows_index>

## Workflows

All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| workflow-a.md | [What it does] |
| workflow-b.md | [What it does] |
</workflows_index>
```

## Step 7: Verify Nothing Was Lost

Compare the original skill against the new structure:

- [ ] All principles preserved (now inline in SKILL.md)
- [ ] All procedures preserved (now in workflows)
- [ ] All knowledge preserved (now in references)
- [ ] No orphaned content
- [ ] All cross-references resolve to real files

## Step 8: Run Validation

```bash
skills-ref validate {skill-path}
```

Fix any errors before declaring done.
</process>

<success_criteria>
Upgrade is complete when:

- [ ] `workflows/` directory exists with at least one workflow file
- [ ] `references/` directory exists (if knowledge was extracted)
- [ ] SKILL.md rewritten as router with `<essential_principles>`, `<intake>`, `<routing>`
- [ ] Essential principles are inline in SKILL.md (not only in reference files)
- [ ] All original content preserved and reachable
- [ ] Intake routes to the correct workflow for each user intent
- [ ] `skills-ref validate` passes
</success_criteria>
