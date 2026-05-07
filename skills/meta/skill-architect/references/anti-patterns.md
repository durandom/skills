# Skill Anti-Patterns

Common failures and how to fix them.

---

## Discovery Failures

### CSO Problem (Context Selection Omission)

**Symptom:** The skill exists but never triggers.

**Cause:** The `description` field is too vague, too generic, or uses first/second person that reads oddly inside `<available_skills>` XML.

**Fix:**
- Use third person: "Audits skills" not "I audit skills" or "You can use this to audit"
- Include specific trigger phrases users would type
- Add "Use when..." with concrete scenarios
- Be slightly pushy — Claude under-triggers more than over-triggers

```yaml
# BAD
description: Helps with skill creation and management.

# GOOD
description: Design, audit, and improve Claude Code skills. Use when creating
  a new skill, reviewing a SKILL.md for issues, choosing between skill
  architectures, or optimizing a skill description for better triggering.
```

### Description Summarizes the Workflow

**Symptom:** Description reads like a table of contents.

**Fix:** Description should describe *what* and *when*, not *how*. The "how" is in SKILL.md body.

---

## Structure Failures

### Skippable Principles

**Symptom:** Essential principles are in a `references/` file, not inline in SKILL.md.

**Why it matters:** Claude only reads SKILL.md when the skill first activates. Reference files are loaded on demand. If a principle lives only in a reference file, it can be skipped.

**Fix:** Essential principles that must always apply go inline in SKILL.md inside `<essential_principles>`.

### Monolithic Skill

**Symptom:** Single SKILL.md over 500 lines, covering multiple distinct workflows.

**Fix:** Upgrade to router pattern. Use `workflows/upgrade-to-router.md`.

### Mixed Concerns

**Symptom:** Procedures and domain knowledge in the same file.

**Fix:**
- Procedures → `workflows/`
- Knowledge/patterns/examples → `references/`

### Nested Reference Chains

**Symptom:** SKILL.md → reference-a.md → reference-b.md → actual info

**Fix:** Keep references one level deep from SKILL.md. Agent may only preview deeply nested files.

---

## Content Failures

### Rigid Rules Without Reasoning

**Symptom:** Lots of ALWAYS/NEVER in all caps; rules with no explanation.

**Why it matters:** Rules without reasoning break at the edges. Claude cannot adapt rules it doesn't understand to novel situations.

**Fix:** Explain *why*. "Use pdfplumber because it handles malformed PDFs better" is more useful than "ALWAYS use pdfplumber."

### Explaining What Claude Already Knows

**Symptom:** Explaining basic programming concepts, standard library usage, well-known tools.

**Fix:** Trust Claude's training. Only add context Claude doesn't already have.

```markdown
# BAD (~150 tokens wasted)
PDF files are a common format for documents. To extract text, we use
pdfplumber, a Python library. First, import it at the top of your file...

# GOOD (~30 tokens)
Extract text with pdfplumber:
```python
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

### Vague Steps

**Symptom:** "Handle the error appropriately" / "Do the thing" / "Follow best practices"

**Fix:** Steps should be specific enough that a fresh invocation can execute them without asking.

### Untestable Success Criteria

**Symptom:** "User is satisfied" / "Skill works well"

**Fix:** Success criteria should be checkable: file exists, tests pass, output matches format, `skills-ref validate` passes.

### Offering Too Many Options

**Symptom:** "You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image..."

**Fix:** Pick a good default with a clear escape hatch:
> Use pdfplumber. For scanned PDFs requiring OCR, use pdf2image + pytesseract instead.

---

## Script Failures

### Interactive Prompts

**Symptom:** Script blocks waiting for user input; agent hangs.

**Fix:** Accept all input via flags, env vars, or stdin. See `references/script-design.md`.

### Opaque Error Messages

**Symptom:** "Error: invalid input" — agent doesn't know what to fix.

**Fix:** "Error: --format must be one of: json, csv, table. Received: xml"

### Unscoped `allowed-tools: Bash`

**Symptom:** `allowed-tools` grants unrestricted shell access.

**Fix:** Scope to specific commands: `Bash(git:*)` not `Bash`.

### Absolute Script Paths

**Symptom:** Script path hardcoded to `.claude/skills/my-skill/scripts/tool` — breaks when installed elsewhere.

**Fix:** Use relative paths from SKILL.md + explain path resolution, or use `${CLAUDE_SKILL_DIR}`.

---

## Routing Failures

### Missing Intake Question

**Symptom:** Complex multi-workflow skill with no "what do you want to do?" question.

**Fix:** Add `<intake>` with numbered options and "Wait for response before proceeding."

### Broken References

**Symptom:** Workflow says "read references/foo.md" but that file doesn't exist.

**Fix:** Run `skills-ref validate` after every structural change to catch dangling references. Also manually verify all paths.

### Redundant Content

**Symptom:** Same information in multiple places — SKILL.md, a workflow, and a reference.

**Fix:** Each piece of information has exactly one home. Reference it from other places rather than duplicating.
