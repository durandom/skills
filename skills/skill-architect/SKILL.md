---
name: skill-architect
description: Design, audit, and improve Claude Code skills (SKILL.md files). Helps
  choose skill architecture (simple, router, domain-expertise), audit existing skills
  against the Agent Skills spec, add components (workflows, references, templates,
  scripts), upgrade simple skills to router pattern, and optimize descriptions for
  better triggering accuracy. For skill creation and eval loops, delegates to
  Anthropic's skill-creator. Use when creating a new skill, reviewing a SKILL.md
  for issues, asking what architecture to use, fixing a skill that never triggers,
  adding a component to an existing skill, or improving any aspect of a skill.
allowed-tools: Skill(skill-creator)
compatibility: skill-creator recommended for creation and description optimization workflows. Audit, upgrade, and add-component workflows work without it. Designed for Claude Code.
---

<essential_principles>

## How Skills Work

### 1. Skills Are Prompts

A skill is not documentation — it is a prompt injection. Everything added competes for the context window. Only include context Claude doesn't already have.

### 2. SKILL.md Is Always Loaded

When a skill activates, Claude reads SKILL.md — guaranteed. Essential principles belong here (inline). Workflow-specific content belongs in `workflows/`. Reusable knowledge belongs in `references/`. This is progressive disclosure.

### 3. Description Drives Discovery

The `description` field is the **only** thing Claude reads at discovery time. A great skill that never triggers is useless. Third person. What + when. Specific trigger phrases. Slightly pushy — Claude under-triggers more than over-triggers.

### 4. Both Format Styles Are Valid

The old `create-agent-skills` skill mandated "pure XML, no markdown headings." This is wrong. The agentskills spec has **no format restrictions**. Anthropic uses markdown headings in all their official skills. XML works well for complex orchestration. Choose based on complexity, not convention.

### 5. Explain WHY, Not Just What

Avoid rigid ALWAYS/NEVER rules without reasoning. LLMs generalize from principles better than from rigid rules. If you find yourself writing ALWAYS in all caps, explain *why* instead.

</essential_principles>

<intake>
What would you like to do?

1. **Choose architecture** — decide between simple, router, or domain-expertise pattern
2. **Create a new skill** — gather intent, choose architecture, delegate to skill-creator
3. **Create a domain expertise skill** — full lifecycle (build/debug/test/optimize/ship)
4. **Audit an existing skill** — check against spec, generate report, offer fixes
5. **Add a component** — add a workflow, reference, template, or script to an existing skill
6. **Upgrade to router** — convert a simple skill to router pattern
7. **Optimize description** — improve triggering accuracy via skill-creator's eval loop
8. **Get guidance** — help with a specific question about skill design or best practices

**Wait for response before proceeding.**
</intake>

<routing>

| Response | Workflow |
|----------|----------|
| 1, "architecture", "which pattern", "what kind" | `workflows/choose-architecture.md` |
| 2, "create", "new", "build", "make" | `workflows/create-skill.md` |
| 3, "domain", "expertise", "lifecycle", "full lifecycle" | `workflows/create-domain-expertise.md` |
| 4, "audit", "check", "review", "analyze" | `workflows/audit-skill.md` |
| 5, "add", "component", "workflow", "reference", "template", "script" | `workflows/add-component.md` |
| 6, "upgrade", "router", "convert", "refactor" | `workflows/upgrade-to-router.md` |
| 7, "optimize", "description", "triggering", "discovery", "CSO" | `workflows/optimize-description.md` |
| 8, "guidance", "help", "question", "advice" | Answer from references — read `references/writing-philosophy.md` and `references/architecture-patterns.md` |

**Intent-based routing (if the user provides clear intent without selecting a menu item):**

- "create a skill for X", "build a new skill", "I need a skill that..." → `workflows/create-skill.md`
- "audit this skill", "what's wrong with my skill", "check my SKILL.md" → `workflows/audit-skill.md`
- "what architecture should I use", "simple or router?", "should I use XML?" → `workflows/choose-architecture.md`
- "add a workflow to my skill", "add a reference", "add a script" → `workflows/add-component.md`
- "my skill never triggers", "skill isn't being used", "fix description" → `workflows/optimize-description.md`
- "upgrade this skill", "convert to router" → `workflows/upgrade-to-router.md`
- "create a domain expertise skill", "full lifecycle skill", "comprehensive domain skill" → `workflows/create-domain-expertise.md`

**After reading the workflow, follow it exactly.**
</routing>

<skill_creator_integration>

## skill-creator is the Primary Creation Tool

Anthropic's `skill-creator` skill handles all creation, eval loops, and description optimization. **skill-architect handles architecture decisions and auditing; skill-creator handles building and testing.** Never substitute skill-architect's own templates for skill-creator unless skill-creator is genuinely unavailable.

### Prerequisite check

skill-creator must be installed as a project skill. Check before any creation or optimization workflow:

```bash
ls .claude/skills/skill-creator/SKILL.md 2>/dev/null || echo "NOT FOUND"
```

If not found, stop and tell the user: "skill-creator must be installed in `.claude/skills/skill-creator/` before I can proceed with skill creation or description optimization. Auditing, upgrading, and adding components work without it."

### Once confirmed available

Read `.claude/skills/skill-creator/SKILL.md` and proceed under its guidance.

</skill_creator_integration>

<quick_reference>

## Spec Cheat Sheet

```yaml
---
name: skill-name              # lowercase+hyphens, max 64 chars, matches directory
description: ...              # max 1024 chars, third person, what+when+triggers
license: Apache-2.0           # optional
compatibility: Requires git   # optional, max 500 chars
allowed-tools: Bash(git:*) Read  # optional, experimental — scope narrowly
metadata:                     # optional, string-to-string map
  author: my-org
---
```

**Validate:** `skills-ref validate path/to/skill`

**Three patterns:**
- **Simple** — one intent, single SKILL.md, under 200 lines
- **Router** — multiple intents, workflows/ + references/, intake+routing in SKILL.md
- **Domain expertise** — full lifecycle, exhaustive references, for both direct use and knowledge loading

</quick_reference>

<reference_index>

## Domain Knowledge

All in `references/`:

**Spec:** spec-fields.md — all frontmatter fields, constraints, Claude Code extensions
**Architecture:** architecture-patterns.md — three patterns and decision tree
**Philosophy:** writing-philosophy.md — why skills are prompts, format choices, conciseness
**Scripts:** script-design.md — when to bundle scripts, agent-friendly design
**Failures:** anti-patterns.md — common issues and how to fix them

</reference_index>

<workflows_index>

## Workflows

All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| choose-architecture.md | Decide between simple, router, domain-expertise |
| create-skill.md | Create a new skill (delegates to skill-creator) |
| create-domain-expertise.md | Build a full-lifecycle domain skill |
| audit-skill.md | Check skill against spec; generate report |
| add-component.md | Add workflow, reference, template, or script |
| upgrade-to-router.md | Convert simple skill to router pattern |
| optimize-description.md | Improve description for triggering accuracy |

</workflows_index>
