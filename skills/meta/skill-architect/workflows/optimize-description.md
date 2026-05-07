# Workflow: Optimize a Skill's Description

<required_reading>
Read first:

1. `references/spec-fields.md` — description field constraints and rules
2. `references/anti-patterns.md` — CSO problem and discovery failures
</required_reading>

<process>

The `description` field is the **only** thing Claude reads when deciding whether to use a skill. A great skill that never triggers is useless. This is the "CSO problem" (Context Selection Omission) — the most common cause of skill abandonment.

## Step 1: Assess the Current Description

Read the skill's current description. Flag issues:

**Discovery failures:**
- Vague language ("helps with", "assists with", "handles")
- No trigger phrases (what would a user actually type?)
- First/second person ("I can help you...", "You can use this to...")
- Summarizes the workflow instead of stating what+when
- Under ~100 chars (probably not enough trigger coverage)
- Over 1024 chars (spec limit — will fail validation)

**Format issues:**
- Starts with skill name ("skill-creator helps create skills...")
- Passive voice throughout
- Technical jargon without user-facing synonyms

## Step 2: Delegate to skill-creator's Description Optimizer

`skill-creator` has a full optimization loop for descriptions. It:
1. Generates 20 eval queries (mix of should-trigger and should-not-trigger)
2. Reviews queries with user for accuracy
3. Runs an automated optimization loop (`scripts/run_loop.py`)
4. Evaluates across train + held-out test sets (5 iterations)
5. Returns the best-performing description

Check that skill-creator is installed:
```bash
ls .claude/skills/skill-creator/SKILL.md 2>/dev/null || echo "NOT FOUND — install skill-creator first"
```

If not found, stop: "Please install skill-creator as a project skill in `.claude/skills/skill-creator/` before proceeding."

Read `.claude/skills/skill-creator/SKILL.md` and invoke its "Description Optimization" section with:
> "I want to optimize the description for my skill `{skill-name}`. Current description: `{description}`. The skill does: {what it does}. Typical triggers: {example user phrases}."

### If skill-creator is not available: manual improvement

Apply these rules to rewrite the description:

**Structure:** `[What it does]. [When to use it, with specific trigger phrases.]`

**Rules:**
1. **Third person** — not "I" or "you"
2. **Active verbs** — "Audits", "Creates", "Optimizes", not "Can be used to audit"
3. **Include the domain noun users would say** — if users say "SKILL.md" include that; if they say "agent skill" include that
4. **Specific triggers** — phrases a real user would type, not abstract category names
5. **Edge cases and synonyms** — if the skill handles multiple related things, name them
6. **Be pushy about triggering** — Claude under-triggers. Add "Use when..." with multiple concrete scenarios

**Before/after example:**

```yaml
# BEFORE: vague, no triggers
description: Helps with skill creation and management.

# AFTER: specific, trigger-rich
description: Design, audit, and improve Claude Code skills (SKILL.md files). Helps
  choose between simple, router, and domain-expertise architectures; audit existing
  skills against the spec; add workflows, references, or scripts; upgrade simple
  skills to router pattern; and optimize skill descriptions for better triggering.
  Use when creating a new skill, reviewing a SKILL.md, fixing a skill that never
  triggers, or asking what architecture to use.
```

## Step 3: Test the Updated Description

Manual test — for each scenario that should trigger the skill, verify the description would lead Claude to choose it:

- Does it include the words the user would use?
- Does it distinguish this skill from other nearby skills?
- Would a reasonable Claude model pick this skill given this description and a typical trigger prompt?

For automated testing, use skill-creator's `run_loop.py` as described above.

## Step 4: Apply and Validate

Update the SKILL.md frontmatter:

```bash
# Verify spec compliance after update
skills-ref validate {skill-path}
```

- Description must be under 1024 chars
- No unexpected frontmatter fields added
</process>

<success_criteria>
Description optimization is complete when:

- [ ] Current description analyzed for CSO issues
- [ ] Updated description is third person, specific, trigger-rich
- [ ] skill-creator optimization loop run (or manual rewrite applied)
- [ ] `skills-ref validate` passes (description under 1024 chars)
- [ ] Tested against representative trigger and non-trigger prompts
</success_criteria>
