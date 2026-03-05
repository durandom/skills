# Agent Skills Spec: Field Reference

Complete reference for SKILL.md frontmatter fields, including Claude Code extensions.

---

## Required Fields

### `name`

**Constraints:** 1–64 chars, lowercase `a-z`, digits `0-9`, hyphens only. No leading/trailing/consecutive hyphens. Must match the parent directory name exactly.

```yaml
name: pdf-processing       # valid
name: PDF-Processing       # invalid: uppercase
name: pdf--processing      # invalid: consecutive hyphens
name: -pdf                 # invalid: leading hyphen
```

**Naming conventions:** verb-noun pairs are most discoverable — `create-*`, `manage-*`, `audit-*`, `optimize-*`. Gerund form also works: `analyzing-spreadsheets`.

---

### `description`

**Constraints:** 1–1024 chars. Non-empty. This is the **primary triggering mechanism** — it is the only thing Claude reads at discovery time.

Rules:
- **Third person** — avoid "I can help" or "You can use"; these read ambiguously inside `<available_skills>` XML
- Include **what it does** AND **when to use it** (specific trigger phrases)
- Be slightly "pushy" about when to trigger — Claude under-triggers more often than over-triggers

```yaml
# BAD: vague, no triggers
description: Helps with documents

# GOOD: specific, includes trigger contexts
description: Extracts text and tables from PDF files, fills PDF forms, and merges
  documents. Use when working with PDF files or when the user mentions PDFs,
  forms, or document extraction.
```

---

## Optional Fields

### `license`

License name or path to a bundled license file. Short string.

```yaml
license: Apache-2.0
license: Proprietary. See LICENSE.txt
```

---

### `compatibility`

**Constraints:** 1–500 chars. Use only if the skill has real environment requirements.

```yaml
compatibility: Designed for Claude Code. Requires git, docker, and internet access.
compatibility: Requires Python 3.11+ and uv
```

Most skills do not need this field.

---

### `allowed-tools` (Claude Code extension, experimental)

Space-delimited list of tools pre-approved to run without user confirmation. Scoping matters — prefer narrow scopes.

```yaml
# Good: scoped to specific commands
allowed-tools: Bash(git:*) Bash(jq:*) Read

# Avoid: too broad
allowed-tools: Bash
```

Supported tool specifiers:
- `Read` — file reading
- `Write` — file writing
- `Bash` — unrestricted shell (avoid)
- `Bash(git:*)` — git commands only
- `Bash(npm:*)` — npm commands only
- `Glob` — file pattern matching
- `Grep` — content search
- `Skill(skill-name)` — invoke another skill

Use `allowed-tools` for deterministic read-only or well-scoped operations. Avoid for anything destructive or interactive.

---

### `metadata`

Arbitrary string-to-string key-value map. Use for client-specific data.

```yaml
metadata:
  author: my-org
  version: "1.2"
  category: productivity
```

---

## Claude Code-Specific Extensions

These are not in the base spec but are supported by Claude Code:

### `context: fork`

Tells Claude Code to fork a new context when invoking this skill. Useful for skills that should start with a clean slate.

```yaml
context: fork
```

### `agent:` / `disable-model-invocation`

Prevents the skill from invoking the AI model directly — used for pure-tool or side-effecting skills where you want deterministic execution only.

```yaml
disable-model-invocation: true
```

### `${CLAUDE_SKILL_DIR}` in scripts

When skills bundle scripts, use `${CLAUDE_SKILL_DIR}` to reference the skill's own directory — this resolves correctly regardless of where Claude Code is installed.

```bash
# In a script referenced from SKILL.md:
SCRIPT_DIR="${CLAUDE_SKILL_DIR}/scripts"
```

Or in SKILL.md text, explain that script paths are relative to the SKILL.md file location (not the working directory). See `references/script-design.md` for the full pattern.

---

## Validation

Run `skills-ref validate` to check your skill against all spec rules:

```bash
# If skills-ref is on your PATH:
skills-ref validate path/to/my-skill

# Or via uvx (no install needed):
uvx skills-ref validate path/to/my-skill
```

What it checks:
- `SKILL.md` exists
- YAML frontmatter is valid
- `name` and `description` present and non-empty
- `name` format rules (lowercase, no `--`, matches directory)
- `description` under 1024 chars
- `compatibility` under 500 chars (if present)
- No unexpected frontmatter fields

---

## Cheat Sheet

| Field | Required | Max Length | Key Rule |
|-------|----------|------------|----------|
| `name` | Yes | 64 chars | Lowercase+hyphens, matches directory |
| `description` | Yes | 1024 chars | Third person, what + when, trigger-rich |
| `license` | No | — | License name or file path |
| `compatibility` | No | 500 chars | Only if real env requirements |
| `allowed-tools` | No | — | Scope narrowly; experimental |
| `metadata` | No | — | String-to-string map |
