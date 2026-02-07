# Recipe: Writing Effective Claude Code Skills

**Target Audience:** AI Coding Agents and developers creating Claude Code skills
**Goal:** Write skills that are concise, discoverable, and effective across all Claude models.

> **Source:** This recipe synthesizes Anthropic's official `skill-creator` skill, production skill patterns from `anthropics/skills`, and the [Agent Skills Specification](https://agentskills.io/specification).

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

### Script Path Resolution

When skills are installed as plugins, Claude Code copies them to a cache directory (`~/.claude/plugins/cache/<name>/<version>/`). Hardcoded paths won't work.

**Use `${CLAUDE_PLUGIN_ROOT}` for portable paths:**

```markdown
<!-- BAD: Hardcoded path breaks when installed as plugin -->
```bash
.claude/skills/my-skill/scripts/process.py
```

<!-- GOOD: Portable path works everywhere -->
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/process.py
```

```

**In SKILL.md, define a variable for convenience:**

```markdown
## CLI Commands

Set the variable for this session:

```bash
MYCLI="${CLAUDE_PLUGIN_ROOT}/scripts/mycli"
```

Then use throughout:

```bash
$MYCLI --help
$MYCLI process file.txt
```

```

**Known issue:** First script execution may fail with "No such file or directory" due to a [Claude Code bug](https://github.com/anthropics/claude-code/issues/11011). Second attempt succeeds. This is not fixable on the skill side.

---

## The Five Principles

### 1. Choose Your Structure: Markdown or XML

Two valid approaches exist. Choose based on complexity:

#### Option A: Markdown Headings (Default)

Used by Anthropic's official skills and most community skills. Simpler and recommended for most cases.

```markdown
## Overview
What the skill does.

## Quick Start
Immediate actionable guidance.

## Workflow
### Step 1: First action
### Step 2: Second action

## Key Guidelines
- Guideline 1
- Guideline 2
```

#### Option B: XML Tags (Advanced)

Used by some community skills (e.g., `xml-standards`) for complex multi-agent orchestration. Provides stronger semantic boundaries.

```xml
<role>
Agent identity and expertise areas.
</role>

<instructions>
Behavioral constraints and workflow phases.
</instructions>

<knowledge>
Domain practices and reusable templates.
</knowledge>

<examples>
Concrete usage scenarios.
</examples>
```

**When to use XML:**

- Complex multi-agent orchestration (dispatchers, planners, implementers)
- Skills that need machine-parseable sections
- Dense, structured instructions where clear boundaries matter

**When to use Markdown:**

- Single-purpose skills
- Human-readable workflows
- Following Anthropic's official patterns

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

## Validating Skills with skills-ref

The [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library provides a CLI and Python API for working with skills. It lives locally at `~/src/durandom/skills/agentskills/skills-ref/`.

### Setup

```bash
cd ~/src/durandom/skills/agentskills/skills-ref
uv sync && source .venv/bin/activate
```

### CLI Usage

```bash
# Validate a skill against the spec (name rules, required fields, field limits)
skills-ref validate path/to/my-skill

# Read frontmatter as JSON
skills-ref read-properties path/to/my-skill

# Generate <available_skills> XML for agent system prompts
skills-ref to-prompt path/to/skill-a path/to/skill-b
```

### Python API

```python
from pathlib import Path
from skills_ref import validate, read_properties, to_prompt

# Validate — returns list of error strings (empty = valid)
errors = validate(Path("my-skill"))

# Read frontmatter — returns SkillProperties dataclass
props = read_properties(Path("my-skill"))

# Generate prompt block — returns XML string
xml = to_prompt([Path("skill-a"), Path("skill-b")])
```

### What validation checks

- `SKILL.md` exists in the directory
- YAML frontmatter is valid and properly delimited
- `name` and `description` are present and non-empty
- `name` follows format rules (lowercase, hyphens, max 64 chars, no `--`, matches directory name)
- `description` is under 1024 chars
- `compatibility` is under 500 chars (if present)
- No unexpected frontmatter fields (only `name`, `description`, `license`, `compatibility`, `allowed-tools`, `metadata` allowed)

---

## How Agents Discover and Activate Skills

Understanding this helps write better `description` fields and structure skills for efficient context usage.

### The progressive disclosure protocol

1. **Discovery** (~100 tokens per skill): At startup, agents load only `name` and `description` from each skill's frontmatter into the system prompt as XML:

```xml
<available_skills>
<skill>
<name>pdf-processing</name>
<description>Extracts text and tables from PDF files...</description>
<location>/path/to/pdf-processing/SKILL.md</location>
</skill>
</available_skills>
```

1. **Activation** (<5000 tokens recommended): When a task matches a skill's description, the agent reads the full `SKILL.md` at the `<location>` path.

2. **Execution** (as needed): The agent follows instructions, loading `scripts/`, `references/`, or `assets/` files on demand.

**Implication for authors:** Your `description` is the only thing competing for attention against potentially 100+ other skills at discovery time. Make it count.

### Integration approaches

- **Filesystem-based agents** (e.g., Claude Code): Activate skills by reading the file at `<location>` (e.g., `cat /path/to/SKILL.md`). Most capable option.
- **Tool-based agents**: Implement dedicated tools to trigger skills and access bundled assets. The `<location>` field can be omitted.

Use `skills-ref to-prompt` to generate the `<available_skills>` XML block for either approach.

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

Per the [Agent Skills Specification](https://agentskills.io/specification):

```yaml
---
name: skill-name              # Required. lowercase-with-hyphens, max 64 chars
description: ...              # Required. Max 1024 chars, non-empty, third person
license: Apache-2.0           # Optional. License name or reference to bundled file
compatibility: Requires git   # Optional. Max 500 chars. Environment requirements
allowed-tools: Bash(git:*) Read  # Optional (experimental). Space-delimited pre-approved tools
metadata:                     # Optional. Arbitrary key-value pairs for client-specific data
  author: example-org
  version: "1.0"
---
```

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64 chars. Lowercase letters, numbers, hyphens. Must match parent directory name. |
| `description` | Yes | Max 1024 chars. Non-empty. What + when to use. |
| `license` | No | License name or reference to bundled license file. |
| `compatibility` | No | Max 500 chars. Intended product, system packages, network access, etc. |
| `allowed-tools` | No | Space-delimited list of pre-approved tools. (Experimental) |
| `metadata` | No | String-to-string key-value mapping for additional properties. |

### Name validation rules

- Only Unicode lowercase alphanumeric characters and hyphens (`a-z`, `0-9`, `-`)
- Cannot start or end with `-`
- No consecutive hyphens (`--`)
- **Must match the parent directory name** (e.g., `name: pdf-processing` requires the directory to be `pdf-processing/`)

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
| **Format** | Markdown headings (default) or XML tags (complex agents) |
| **Length** | SKILL.md under 500 lines |
| **Frontmatter** | `name` + `description` required; `license`, `compatibility`, `allowed-tools`, `metadata` optional |
| **Name** | Lowercase + hyphens, max 64 chars, must match directory name |
| **Description** | Third person, what + when, specific triggers, max 1024 chars |
| **References** | One level deep from SKILL.md |
| **Script Paths** | Use `${CLAUDE_PLUGIN_ROOT}/scripts/...` for portability |
| **Freedom** | High for creative, Low for fragile operations |
| **Validation** | `skills-ref validate path/to/skill` before publishing |
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

**Official:**

- [Agent Skills Specification](https://agentskills.io/specification) — The canonical format definition
- [Agent Skills Documentation](https://agentskills.io) — Guides, tutorials, and integration docs
- [skills-ref Reference Library](https://github.com/agentskills/agentskills/tree/main/skills-ref) — Validation CLI and Python API (local: `~/src/durandom/skills/agentskills/skills-ref/`)
- [Anthropic Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference) — `${CLAUDE_PLUGIN_ROOT}` and path resolution
- **Anthropic's `skill-creator` skill** — The authoritative guide in `anthropics/skills`

**Community:**

- [obra/superpowers](https://github.com/obra/superpowers) — Popular skills collection (markdown approach)
- [xml-standards skill](https://claude-plugins.dev/skills/@MadAppGang/claude-code/xml-standards) — XML tags for complex agents
- [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) — First principles analysis
- [meta_skill best practices](https://github.com/Dicklesworthstone/meta_skill) — Skill authoring patterns
