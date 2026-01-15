# Recipe: Writing Effective Claude Code Skills

**Target Audience:** AI Coding Agents and developers creating Claude Code skills
**Goal:** Write skills that are concise, discoverable, and effective across all Claude models.

> **Source:** This recipe synthesizes Anthropic's official `skill-creator` skill and production skill patterns from `anthropics/skills`.

---

## The Core Philosophy: "Skills Are Prompts"

A skill is not documentation—it's a prompt injection. Everything you add competes for the context window with conversation history, other skills, and the user's request.

**The Prime Directive:** Only add context Claude doesn't already have.

Challenge every piece of content:

- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

---

## Skill Structure: Two Patterns

### Pattern 1: Simple Skill (Single File)

Use when the task is straightforward and doesn't require decision branching.

```yaml
---
name: skill-name
description: What it does. Use when [trigger conditions].
---

# Skill Title

## Overview
Clear statement of what this skill accomplishes.

## Quick Start
Immediate actionable guidance—what Claude should do first.

## Workflow
### Step 1: First action
Instructions for step 1.

### Step 2: Second action
Instructions for step 2.

## Key Guidelines
- Guideline 1
- Guideline 2
```

### Pattern 2: Multi-File Skill (With Bundled Resources)

Use when the skill handles multiple workflows or needs extensive reference material.

```
skill-name/
├── SKILL.md              # Main instructions (required)
├── scripts/              # Executable code (Python/Bash)
├── references/           # Documentation loaded as needed
└── assets/               # Files used in output (templates, fonts, etc.)
```

**When to use each folder:**

- **scripts/** — Deterministic code reused repeatedly (e.g., `rotate_pdf.py`)
- **references/** — Documentation Claude reads for context (e.g., `schema.md`, `api_docs.md`)
- **assets/** — Files used in output, not loaded into context (e.g., templates, logos)

---

## The Five Principles

### 1. Standard Markdown Structure

Use standard markdown headings (`#`, `##`, `###`) for skill body. This is the pattern used by all Anthropic production skills.

**Common sections:**

- `## Overview` — What the skill does
- `## Quick Start` — Immediate actionable guidance
- `## Workflow` — Step-by-step process
- `## Key Guidelines` — Important rules

**Keep formatting clean:** Use bold, lists, code blocks within sections.

### 2. Conciseness Is Key

```markdown
<!-- BAD: ~150 tokens, explains what Claude already knows -->
## Quick Start
PDF files are a common file format used for documents. To extract
text from them, we'll use a Python library called pdfplumber...

<!-- GOOD: ~50 tokens, assumes Claude is smart -->
## Quick Start
Extract PDF text with pdfplumber:

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

```

### 3. Degrees of Freedom

Match specificity to task fragility.

| Freedom Level | When to Use | Example |
|--------------|-------------|---------|
| **High** | Creative tasks, multiple valid approaches | Code review, content generation |
| **Medium** | Preferred pattern exists, some variation OK | Report generation with template |
| **Low** | Fragile operations, exact sequence required | Database migrations, payment processing |

**Low freedom example:**
```markdown
## Migration Workflow
Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

**Do not modify the command or add additional flags.**

```

### 4. Progressive Disclosure

Keep SKILL.md under 500 lines. Split details into reference files.

**Token usage scales with task complexity:**
- Simple task: SKILL.md only (~500 tokens)
- Medium task: SKILL.md + one reference (~1000 tokens)
- Complex task: SKILL.md + multiple references (~2000 tokens)

**Keep references one level deep.** Claude may only preview deeply nested files.

```markdown
<!-- GOOD: Direct references from SKILL.md -->
**Form filling**: See [FORMS.md](FORMS.md)
**API reference**: See [REFERENCE.md](REFERENCE.md)

<!-- BAD: Nested references -->
SKILL.md → advanced.md → details.md → actual info
```

### 5. Description Enables Discovery

The `description` field is how Claude decides whether to use your skill from potentially 100+ available skills.

**Rules:**

- Always write in **third person** (not "I can help..." or "You can use...")
- Include **what it does** AND **when to use it**
- Include specific trigger terms

```yaml
# BAD: Vague, no triggers
description: Helps with documents

# GOOD: Specific, includes triggers
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

---

## Validation and Feedback Loops

For complex tasks, use the **plan-validate-execute** pattern:

```markdown
## Form Filling Workflow

Copy this checklist:

```

- [ ] Step 1: Analyze form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)

```

**Validation scripts should:**
- Provide verbose, specific error messages
- Show available valid options when invalid
- Suggest actionable fixes
```

---

## Testing Across Models

What works for Opus might need more detail for Haiku.

| Model | Needs |
|-------|-------|
| **Haiku** | More explicit instructions, complete examples, clear structure |
| **Sonnet** | Balanced detail, clear structure, progressive disclosure |
| **Opus** | Concise instructions, principles over procedures, high freedom |

**Test with all target models.** Start with medium detail, observe where models struggle, adjust.

---

## Anti-Patterns to Avoid

### Don't explain what Claude already knows

```markdown
<!-- BAD -->
PDF files are documents that contain text. To extract...

<!-- GOOD -->
Use pdfplumber for text extraction.
```

### Don't offer too many options

```markdown
<!-- BAD: Confusing -->
You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image...

<!-- GOOD: Default with escape hatch -->
Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Don't include time-sensitive information

```markdown
<!-- BAD: Will become wrong -->
If you're doing this before August 2025, use the old API.

<!-- GOOD: Old patterns section -->
## Current method
Use the v2 API endpoint.

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
The v1 API used: api.example.com/v1/messages
</details>
```

### Don't use Windows-style paths

```markdown
<!-- BAD -->
scripts\helper.py

<!-- GOOD -->
scripts/helper.py
```

---

## YAML Frontmatter Requirements

```yaml
---
name: skill-name          # lowercase-with-hyphens, max 64 chars
                          # No: "anthropic", "claude", XML tags
description: ...          # Max 1024 chars, non-empty, third person
---
```

**Naming conventions:** `create-*`, `manage-*`, `setup-*`, `generate-*`, `build-*`

Or gerund form: `processing-pdfs`, `analyzing-spreadsheets`, `testing-code`

---

## Development Workflow

1. **Complete a task without a skill** — Notice what context you repeatedly provide
2. **Identify the reusable pattern** — What would help future similar tasks?
3. **Write minimal instructions** — Just enough to address gaps
4. **Test with target models** — Observe behavior
5. **Iterate based on observation** — Add detail where Claude struggles, remove where it over-explains

---

## Summary Cheat Sheet

| Aspect | Guidance |
|--------|----------|
| **Structure** | Simple (single file) or Multi-file (with scripts/, references/, assets/) |
| **Format** | Standard markdown headings (`#`, `##`, `###`) |
| **Length** | SKILL.md under 500 lines |
| **Description** | Third person, what + when, specific triggers |
| **References** | One level deep from SKILL.md |
| **Freedom** | High for creative, Low for fragile operations |
| **Validation** | Verbose scripts with actionable error messages |
| **Testing** | All target models (Haiku needs more detail) |

---

## What NOT to Include

A skill should only contain essential files. Do NOT create extraneous documentation:

- ❌ README.md
- ❌ INSTALLATION_GUIDE.md
- ❌ CHANGELOG.md
- ❌ QUICK_REFERENCE.md

The skill should only contain information needed for an AI agent to do the job.

---

## References

- **Anthropic's `skill-creator` skill** — The authoritative guide in `anthropics/skills`
- [Anthropic Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Agent Skills Spec](https://agentskills.io)
