# Skill Writing Philosophy

Core principles for writing effective skills — shared by Anthropic's `skill-creator` and the agentskills spec.

---

## Skills Are Prompts

A skill is not documentation — it is a prompt injection. Everything you add competes for the context window with conversation history, other skills, and the user's request.

**The Prime Directive:** Only add context Claude doesn't already have.

Challenge every piece of content:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

---

## Explain WHY, Not Just What

Anthropic's `skill-creator` is explicit about this: avoid heavy-handed MUSTs. Instead, explain *why* something matters and let Claude reason from that understanding.

**Rigid (avoid):**
> ALWAYS use pdfplumber. NEVER use PyPDF2.

**Principle-based (prefer):**
> pdfplumber handles malformed PDFs more gracefully than PyPDF2 and preserves layout metadata needed for table extraction.

LLMs are smart. They follow principles better than rigid rules when the reasoning is clear. Rigid rules also break down at the edges; principles generalize.

The `skill-creator` authors put it this way: "If you find yourself writing ALWAYS or NEVER in all caps... reframe and explain the reasoning so that the model understands why the thing you're asking for is important."

---

## Format: Markdown or XML — Both Valid

The old `create-agent-skills` skill mandated "pure XML, no markdown headings." This was wrong. The agentskills spec explicitly says: **"There are no format restrictions. Write whatever helps agents perform the task effectively."**

Anthropic uses markdown headings in all their official skills (`skill-creator`, `github`, `create-plans`). Community skills often use XML for complex orchestration.

**Choose based on complexity:**

### Markdown (default)
Best for: single-purpose skills, human-readable workflows, following Anthropic's patterns.

```markdown
## Quick Start
Extract PDF text with pdfplumber:

## Workflow
### Step 1: Open the file
### Step 2: Extract text
```

### XML Tags (advanced)
Best for: complex multi-agent orchestration, skills needing machine-parseable sections, dense structured instructions.

```xml
<essential_principles>
Rules that apply universally.
</essential_principles>

<intake>
Ask the user what they want.
</intake>

<routing>
Map answers to workflows.
</routing>
```

**You can mix them:** XML tags for structural sections (router pattern), markdown within content (lists, code blocks, bold text). This is what most mature skills do.

---

## SKILL.md Is Always Loaded

When a skill activates, Claude reads SKILL.md. This is a guarantee you can rely on:

- **Essential principles go in SKILL.md** — they cannot be skipped
- **Workflow-specific content goes in `workflows/`** — loaded only when needed
- **Reusable knowledge goes in `references/`** — loaded on demand

The router pattern exploits this: SKILL.md sets up principles and asks "what do you want to do?" — only then does it load the appropriate workflow.

---

## Progressive Disclosure

SKILL.md under 500 lines. Split details into reference files. Load only what's needed for the current workflow.

**Token cost scales with task complexity:**
- Simple task: SKILL.md only (~500 tokens)
- Medium task: SKILL.md + one reference (~1000 tokens)
- Complex task: SKILL.md + multiple references (~2000 tokens)

Keep references one level deep from SKILL.md. Avoid deeply nested reference chains.

---

## Description = Discovery

The `description` field is the **only** thing Claude reads at discovery time. It determines whether the skill is ever used. This is the "CSO problem" (Context Selection Optimization): a great skill that never triggers is useless.

Key rules for descriptions:
- **Third person** — "Audits and improves skills" not "I help you audit skills"
- **What + When** — include both what it does and specific triggers
- **Be pushy** — Claude under-triggers more than over-triggers; err toward explicit trigger conditions
- **Include specific phrases** users would actually type

The `skill-creator` has a full optimization loop for this. See `workflows/optimize-description.md`.

---

## Degrees of Freedom

Match specificity to the task's fragility:

| Task type | Freedom | Approach |
|-----------|---------|----------|
| Database migration, payments | Low | Exact steps, specific commands |
| API calls, file processing | Medium | Preferred pattern with flexibility |
| Code review, content generation | High | Principles and heuristics |

Too much freedom on fragile tasks → errors. Too little freedom on creative tasks → rigid, suboptimal outputs.

---

## Conciseness Examples

**Verbose (~150 tokens, over-explains):**
> PDF files are a common file format used for documents. To extract text from them, we'll use a Python library called pdfplumber. First, you'll need to import the library, then open the PDF file using the open method...

**Concise (~50 tokens, assumes Claude is smart):**
> Extract PDF text with pdfplumber:
> ```python
> import pdfplumber
> with pdfplumber.open("file.pdf") as pdf:
>     text = pdf.pages[0].extract_text()
> ```

The concise version works because Claude already knows what PDFs are, what Python imports do, and how to read code.
