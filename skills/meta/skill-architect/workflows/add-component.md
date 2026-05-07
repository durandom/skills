# Workflow: Add a Component to an Existing Skill

<required_reading>
Read first:

1. `references/architecture-patterns.md` — understand folder roles
2. `references/script-design.md` — if adding a script
</required_reading>

<process>

## Step 1: Identify the Skill and Component Type

If not already specified, ask:
- "What skill are you adding to? (path or name)"
- "What type of component? workflow / reference / template / script"

Read the existing SKILL.md to understand the current structure before adding anything.

## Step 2: Adding a Workflow

**When to add:** A new user intent that belongs in this skill — a new "thing a user might want to do."

### Create the workflow file

```bash
# File naming: lowercase-with-hyphens, verb-noun
# workflows/create-skill.md, workflows/audit-skill.md, workflows/upgrade-to-router.md
```

**Workflow file template:**

```markdown
# Workflow: [Name]

<required_reading>
Read before starting:

1. references/[relevant-file].md — [why it's needed]
</required_reading>

<process>

## Step 1: [First action]

[Specific instructions]

## Step 2: [Second action]

[Specific instructions]

## Step N: Verify

[How to confirm it worked]
</process>

<success_criteria>
Done when:

- [ ] [Verifiable criterion 1]
- [ ] [Verifiable criterion 2]
</success_criteria>
```

### Update SKILL.md

Add the workflow to the routing table and workflows index:

```markdown
# In <routing>:
| "keyword1", "keyword2" | workflows/new-workflow.md |

# In <workflows_index>:
| new-workflow.md | [What it does] |
```

Also update the `<intake>` numbered list if the skill uses one.

## Step 3: Adding a Reference

**When to add:** Domain knowledge that multiple workflows need, or that is too detailed for SKILL.md but too important to omit.

### Create the reference file

```bash
# File naming: topic-based
# references/architecture.md, references/api-docs.md, references/patterns.md
```

**Reference file structure (choose based on content type):**

For decision guidance:
```markdown
# [Topic]

## Options

### Option A: [name]
**Use when:** [specific scenarios]
**Strengths:** [what it's good at]
**Weaknesses:** [limitations]

### Option B: [name]
[same structure]

## Decision Tree

If [condition A] → use Option A
If [condition B] → use Option B
```

For patterns/examples:
```xml
<patterns>
<pattern name="Pattern Name">
**Use when:** [scenario]
**Implementation:** [code or steps]
**Trade-offs:** [considerations]
</pattern>
</patterns>
```

### Update SKILL.md

Add to the `<reference_index>`:

```markdown
**[Category]:** new-reference.md — [one-line description of contents]
```

Update any workflow that should read this reference:

```markdown
# In the workflow's <required_reading>:
3. references/new-reference.md — [why this workflow needs it]
```

## Step 4: Adding a Template

**When to add:** The skill produces consistent output structures (plans, specs, reports, configs) where the *shape* matters as much as the content.

### Create the template file

```bash
# File naming: descriptive of the output
# templates/audit-report.md, templates/skill-spec.md, templates/config.yaml
```

Templates use `{{PLACEHOLDER}}` syntax:

```markdown
# {{TITLE}}

## Summary
{{One-paragraph summary of findings}}

## Details
{{Detailed section - bullets or prose as appropriate}}

## Next Steps
- [ ] {{First action item}}
- [ ] {{Second action item}}
```

### Update SKILL.md

Add to reference_index or a dedicated templates section:

```markdown
**Templates:** templates/my-template.md — [when to use it]
```

Update the relevant workflow to reference the template:

```markdown
Use the template at `templates/my-template.md` — copy it and fill in the placeholders.
```

## Step 5: Adding a Script

**When to add:** Reusable code that the skill runs repeatedly, or operations error-prone if rewritten from scratch each time.

### Create the script

Follow `references/script-design.md` patterns:

```python
#!/usr/bin/env python3
# /// script
# dependencies = ["requests>=2.31"]
# ///
"""
Brief description of what this script does.

Usage: scripts/my-script.py [OPTIONS] INPUT

Options:
  --format FORMAT   Output format: json, table (default: json)
  --output FILE     Write to FILE instead of stdout

Exit codes: 0=success, 1=not-found, 2=invalid-args
"""
import argparse
import sys
# ...
```

### Update SKILL.md

List the script and its path resolution:

    ## Available scripts

    - **`scripts/my-script.py`** — [What it does]

    Script paths are relative to this SKILL.md file. Run with:

        uv run scripts/my-script.py --help

Update the relevant workflow to use the script.

## Step 6: Verify the Addition

- [ ] New file exists at the expected path
- [ ] SKILL.md updated (routing, index, or references as appropriate)
- [ ] All cross-references in workflows and SKILL.md point to real files
- [ ] Run `skills-ref validate {skill-path}` if available
</process>

<success_criteria>
Component addition is complete when:

- [ ] New file created with appropriate structure
- [ ] SKILL.md updated to reference the new component
- [ ] No dangling references (all paths point to real files)
- [ ] Validation passes
</success_criteria>
