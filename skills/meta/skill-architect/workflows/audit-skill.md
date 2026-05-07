# Workflow: Audit a Skill

<required_reading>
Read these reference files before auditing:

1. `references/spec-fields.md` — full field requirements
2. `references/architecture-patterns.md` — structure expectations
3. `references/anti-patterns.md` — common issues to flag
</required_reading>

<process>

## Step 1: Locate the Skill

If the user hasn't specified a path, list available skills:

```bash
ls .claude/skills/
ls skills/          # if in a skills plugin repo
```

Ask: "Which skill would you like to audit? (path or name)"

## Step 2: Read the Full Skill Structure

```bash
# Read SKILL.md
cat {skill-path}/SKILL.md

# Check what else exists
ls {skill-path}/
ls {skill-path}/workflows/ 2>/dev/null
ls {skill-path}/references/ 2>/dev/null
ls {skill-path}/scripts/ 2>/dev/null
```

Read any referenced workflow and reference files that are relevant.

## Step 3: Run the Audit Checklist

### Frontmatter

- [ ] `name` field present (lowercase-with-hyphens, max 64 chars, no `--`)
- [ ] `name` matches parent directory name
- [ ] `description` present, non-empty, under 1024 chars
- [ ] `description` is third person (not "I can..." or "You can...")
- [ ] `description` says **what it does AND when to use it**
- [ ] `allowed-tools` (if present) is scoped narrowly — `Bash(git:*)` not `Bash`
- [ ] `compatibility` (if present) only states real env requirements
- [ ] No unexpected frontmatter fields (only: name, description, license, compatibility, allowed-tools, metadata)

### Structure

- [ ] SKILL.md under 500 lines
- [ ] Essential principles are **inline in SKILL.md** (not only in a reference file)
- [ ] All referenced workflow files exist
- [ ] All referenced reference files exist
- [ ] References are one level deep (no nested chains)

### Router Pattern (if complex skill with multiple workflows)

- [ ] Has `<intake>` or equivalent "what do you want to do?" question
- [ ] Has routing table mapping answers to workflows
- [ ] All workflow files in routing table exist
- [ ] Routing includes intent-based fallback (not just numbered responses)

### Workflow Files (if present)

- [ ] Each workflow has a `required_reading` section listing references to load
- [ ] Each workflow has a `process` section with specific steps (not vague)
- [ ] Each workflow has `success_criteria` that are verifiable (not "user is satisfied")
- [ ] All reference files in `required_reading` sections exist

### Content Quality

- [ ] Steps are specific — not "handle it appropriately" or "follow best practices"
- [ ] No rigid ALWAYS/NEVER rules without explanation of *why*
- [ ] No explaining things Claude already knows (basic programming, standard tools)
- [ ] Success criteria are checkable (file exists, tests pass, validate succeeds)
- [ ] No redundant content across files (each fact has one home)
- [ ] No time-sensitive information that will become stale

### Script Files (if present)

- [ ] Scripts have `--help` output
- [ ] Scripts have no interactive prompts
- [ ] Error messages are descriptive (not just "Error")
- [ ] Script path resolution explained in SKILL.md
- [ ] Scripts are idempotent (safe to retry)

### New Spec Fields (check if skill is missing these)

- [ ] `allowed-tools` considered for skills that use predictable tools
- [ ] `${CLAUDE_SKILL_DIR}` used for script paths (vs hardcoded `.claude/skills/...`)
- [ ] `context: fork` considered for skills that benefit from clean context
- [ ] `skills-ref validate` run to catch spec violations

## Step 4: Generate Report

```
## Audit Report: {skill-name}

### Passing
- [list each passing item concisely]

### Issues Found

1. **[Issue name]**: [What the problem is]
   → Fix: [Specific action to take]

2. **[Issue name]**: [What the problem is]
   → Fix: [Specific action to take]

### Score: X/Y criteria passing

### Priority fixes:
[Top 1-3 things that would most improve the skill]
```

## Step 5: Run Automated Validation

```bash
# If skills-ref is on your PATH:
skills-ref validate {skill-path}

# Or via uvx (no install needed):
uvx skills-ref validate {skill-path}
```

Include any validation errors in the report.

## Step 6: Offer Fixes

Ask: "Would you like me to fix these issues?"

1. **Fix all** — Apply all recommended fixes
2. **Fix one by one** — Review each fix before applying
3. **Just the report** — No changes needed

If fixing, make each change, then verify the file is still valid.
</process>

<success_criteria>
Audit is complete when:

- [ ] Full skill structure read (SKILL.md + all referenced files)
- [ ] All checklist items evaluated
- [ ] Report presented with specific issues and fixes
- [ ] `skills-ref validate` run (if available)
- [ ] Fixes applied if requested
</success_criteria>
