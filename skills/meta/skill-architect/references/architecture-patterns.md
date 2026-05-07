# Skill Architecture Patterns

Three patterns cover essentially all skill use cases. Choose based on complexity, not preference.

---

## Pattern 1: Simple Skill (Single File)

**Use when:** One clear purpose, single workflow, no branching user intent.

```
skill-name/
└── SKILL.md
```

**Size target:** Under 200 lines.

**Signs you need this pattern:**
- One thing the user wants to accomplish
- No "what would you like to do?" decision needed
- Instructions fit in one document without crowding

**Example SKILL.md structure:**
```yaml
---
name: skill-name
description: Does X. Use when the user needs to do X.
---

## Overview
What this skill does.

## Quick Start
Immediate guidance.

## Workflow
Step-by-step instructions.

## Key Guidelines
- Guideline 1
- Guideline 2
```

Or with XML tags (both formats valid — see `references/writing-philosophy.md`):
```xml
<objective>What the skill does</objective>
<quick_start>Immediate guidance</quick_start>
<process>Steps...</process>
<success_criteria>Done when...</success_criteria>
```

---

## Pattern 2: Router Skill (Multi-Workflow)

**Use when:** Multiple distinct user intents share essential principles and/or domain knowledge.

```
skill-name/
├── SKILL.md              # Router: principles + intake + routing
├── workflows/            # One file per user intent (FOLLOW)
├── references/           # Shared domain knowledge (READ)
├── templates/            # Output structures to copy and fill
└── scripts/              # Reusable executable code (EXECUTE)
```

**Signs you need this pattern:**
- User needs to choose: "create? audit? add component? optimize?"
- Multiple workflows share principles that must always apply
- Reference material is useful across multiple workflows
- Skill is likely to grow over time

**SKILL.md structure for router:**
```
YAML frontmatter
<essential_principles>   — Always applies, inline (can't be skipped)
<intake>                 — Ask the user what they want
<routing>                — Maps answers to workflows
<quick_reference>        — Optional: always-visible cheat sheet
<reference_index>        — List of reference files
<workflows_index>        — List of workflow files
```

**Key insight:** The router SKILL.md should stay under 500 lines. The router's job is to load the right workflow — not to contain all the knowledge itself.

---

## Pattern 3: Domain Expertise Skill (Full Lifecycle)

**Use when:** Comprehensive coverage of a domain is needed — build, debug, test, optimize, ship.

```
domain-name/
├── SKILL.md              # Router for the full lifecycle
├── workflows/
│   ├── build-new.md
│   ├── add-feature.md
│   ├── debug.md
│   ├── write-tests.md
│   ├── optimize.md
│   └── ship.md
└── references/           # Exhaustive domain knowledge
    ├── architecture.md
    ├── libraries.md
    ├── patterns.md
    ├── testing.md
    ├── performance.md
    └── anti-patterns.md
```

**Signs you need this pattern:**
- Covers a full technology domain (macOS apps, Python games, web scraping)
- Users need to go from "starting fresh" to "shipped"
- Reference material is extensive and domain-specific
- Skill may be loaded by other skills (like `create-plans`) for domain knowledge

**What makes it different from Pattern 2:**
- Workflows cover the entire lifecycle, not just one aspect
- References are exhaustive, not just supporting material
- It can be invoked directly by users AND loaded for knowledge by other skills

---

## Decision Tree

```
What is the user trying to accomplish?

One specific thing, no branching intent
  └─ Pattern 1: Simple Skill
     (If it grows past 200 lines → upgrade to Pattern 2)

Multiple things, shared principles
  └─ Pattern 2: Router Skill

Everything in a domain, full lifecycle
  └─ Pattern 3: Domain Expertise Skill
```

---

## Common Upgrade Path

Most skills start as Pattern 1 and grow into Pattern 2 when they:
- Exceed 200 lines
- Add a second distinct workflow
- Accumulate shared knowledge that multiple workflows need

Use the `workflows/upgrade-to-router.md` workflow to perform this upgrade safely.

---

## Folder Roles

| Folder | Role | Verb |
|--------|------|------|
| `workflows/` | Step-by-step procedures | FOLLOW |
| `references/` | Domain knowledge, patterns, examples | READ |
| `templates/` | Output structures to copy and fill | COPY + FILL |
| `scripts/` | Reusable executable code | EXECUTE |

**Key distinction:** `references/` is for *knowledge* Claude needs to reason well. `workflows/` is for *procedures* Claude needs to act. Don't mix them.
