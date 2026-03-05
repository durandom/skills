# Workflow: Create a New Skill

<required_reading>
Read first:

1. `references/architecture-patterns.md` — choose the right pattern
2. `references/writing-philosophy.md` — core principles
3. `references/spec-fields.md` — frontmatter requirements
</required_reading>

<process>

## Step 1: Understand the Intent

**If the user has provided context** (e.g., "build a skill for X"):
- Extract what's already stated, what can be inferred, what's genuinely unclear
- Ask only about real gaps — not things obvious from context

**If no context was provided:**
- Ask: "What should this skill enable Claude to do?"

Useful clarifying questions (ask only those with genuine gaps):
- "What specific operations should this skill handle?" (with options based on domain)
- "When should this skill trigger — what would a user say or be doing?"
- "What's the expected output or deliverable?"
- "Should this also handle [related thing], or stay focused on [core thing]?"

**Decision gate:** After gathering context, ask:
"Ready to proceed, or would you like to clarify more?"

---

## Step 2: Choose Architecture

Use the decision tree from `workflows/choose-architecture.md` (or inline it here):

- One clear user intent, simple → **Simple skill**
- Multiple user intents, shared principles → **Router skill**
- Full domain lifecycle → **Domain expertise skill** → use `workflows/create-domain-expertise.md`

---

## Step 3: Use skill-creator

**Use Anthropic's `skill-creator` skill for all creation, eval, and iteration work.** It handles drafting, test case generation, eval loops, and description optimization far better than any standalone instructions.

### Invoke skill-creator

Read `skill-creator/SKILL.md` (Anthropic's official skill) and hand off with the context gathered:

```bash
# Prerequisite check — must pass before proceeding:
ls .claude/skills/skill-creator/SKILL.md 2>/dev/null || echo "NOT FOUND — install skill-creator first"
```

If not found, stop: "Please install skill-creator as a project skill in `.claude/skills/skill-creator/` and try again."

If found, read `.claude/skills/skill-creator/SKILL.md` and proceed under its guidance:

> "I want to create a skill called `{name}`. It should: {what it does}. Triggers when: {trigger conditions}. Architecture: {simple/router/domain expertise}. Context gathered: {user's context}."

skill-creator will draft the skill, write test cases, run evals (with/without skill comparison), present results for review, iterate, and optimize the description.

### Only if skill-creator is genuinely unavailable

Use the templates in `templates/simple-skill.md` or `templates/router-skill.md` as a starting point. Follow `references/writing-philosophy.md` for principles. Validate with `skills-ref validate {skill-path}`. This path skips the eval loop — recommend installing skill-creator for proper validation.

---

## Step 4: Validate the Result

After `skill-creator` (or manual creation) is done:

```bash
skills-ref validate {skill-path}
```

Check:
- [ ] `name` matches directory
- [ ] `description` is third person, has triggers
- [ ] All referenced files exist
- [ ] SKILL.md under 500 lines
- [ ] For router: intake + routing present

---

## Step 5: Register (Optional)

If this skill is meant to be invoked via a slash command, create a command file:

```bash
cat > .claude/commands/{skill-name}.md << 'EOF'
---
description: {Brief description}
argument-hint: [{what the argument is}]
allowed-tools: Skill({skill-name})
---

Invoke the {skill-name} skill for: $ARGUMENTS
EOF
```
</process>

<success_criteria>
Skill creation is complete when:

- [ ] User intent and architecture decided
- [ ] skill-creator delegated to (or standalone process followed)
- [ ] SKILL.md has valid frontmatter (`skills-ref validate` passes)
- [ ] Description is trigger-optimized (or optimization run via skill-creator's loop)
- [ ] Tested with at least one realistic user prompt
</success_criteria>
