# Workflow: Choose Skill Architecture

<required_reading>
Read first:

1. `references/architecture-patterns.md` — the three patterns in detail
</required_reading>

<process>

## The Architecture Decision

Answer these questions to identify the right pattern:

### Question 1: How many distinct things can a user want to do?

**One clear thing** (e.g., "extract PDF text", "commit with message")
→ Start with **Pattern 1: Simple Skill**
→ If it grows past 200 lines or gains a second user intent, upgrade to Pattern 2

**Multiple things** (e.g., "create? audit? optimize? add component?")
→ **Pattern 2: Router Skill**

**Everything in a domain** (e.g., "build, debug, test, optimize, and ship macOS apps")
→ **Pattern 3: Domain Expertise Skill**

---

### Question 2: Will there be shared principles that must always apply?

**No** — content is workflow-specific
→ Pattern 1 or just flat workflows in Pattern 2

**Yes** — principles like "skills are prompts" or "description drives discovery" apply regardless of which workflow runs
→ These go inline in SKILL.md `<essential_principles>` in Pattern 2 or 3

---

### Question 3: Is there reusable domain knowledge that multiple workflows need?

**No** — each workflow is self-contained
→ Pattern 1 or Pattern 2 without a heavy `references/` directory

**Yes** — multiple workflows share knowledge about the same domain (e.g., spec fields, architecture patterns)
→ Pattern 2 with `references/` directory, OR Pattern 3

---

### Question 4: Does it need to cover a full lifecycle?

**No** — focused on one phase (e.g., just "creating skills")
→ Pattern 1 or Pattern 2

**Yes** — build → debug → test → optimize → ship
**Yes** — needs exhaustive domain knowledge for both direct use and as a knowledge source for other skills
→ Pattern 3: Domain Expertise Skill

---

## Decision Summary

```
One intent, simple task
  → Pattern 1: Simple Skill (single SKILL.md)
     If grows > 200 lines or gains second intent → upgrade to Pattern 2

Multiple intents, shared principles, shared knowledge
  → Pattern 2: Router Skill (SKILL.md + workflows/ + references/)

Full domain coverage, exhaustive knowledge, full lifecycle
  → Pattern 3: Domain Expertise Skill
```

---

## After Choosing

| Pattern | Next step |
|---------|-----------|
| Pattern 1 | Use `workflows/create-skill.md` — it handles simple skills |
| Pattern 2 (task-focused) | Use `workflows/create-skill.md` — select router option |
| Pattern 3 (domain expertise) | Use `workflows/create-domain-expertise.md` |
| Upgrading existing Pattern 1 to Pattern 2 | Use `workflows/upgrade-to-router.md` |

---

## Example Mappings

| What you want to build | Pattern |
|------------------------|---------|
| "A skill that commits with a conventional message" | Pattern 1 |
| "A skill that manages GitHub PRs — create, review, merge, close" | Pattern 2 |
| "A skill for building and shipping macOS apps" | Pattern 3 |
| "A skill that audits other skills" | Pattern 1 (or 2 if it grows) |
| "A skill that routes to skill-creator for creation + handles architecture decisions" | Pattern 2 |
</process>

<success_criteria>
Architecture is chosen when:

- [ ] Pattern identified (1, 2, or 3)
- [ ] Reasoning explained to user
- [ ] Next workflow identified
</success_criteria>
