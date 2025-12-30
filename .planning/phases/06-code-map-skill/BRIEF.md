# Code Map Skill

## Problem

AI agents start every session with zero memory. They waste significant context (and time) just understanding "where am I?" before they can do useful work. Even with CLAUDE.md, agents lack a systematic way to navigate codebases at different abstraction levels.

## Solution

A **code-map** skill that provides:

1. A standardized format for hierarchical codebase documentation (L0-L3 zoom levels)
2. Workflows for creating, updating, and validating maps
3. A bootstrap workflow for agents to quickly orient themselves
4. Templates and validation scripts

## Key Design Decisions

### Zoom Levels

```
L0: ARCHITECTURE.md     # System-wide (1 file, ~500 lines max)
L1: domains/*.md        # Major subsystems (3-10 files, ~300 lines each)
L2: modules/*.md        # Components/services (10-50 files, ~200 lines each)
L3: Source files        # Actual code (no docs needed)
```

### Standard Markdown (Clickable Everywhere)

**Anchors** (in headings, for grep navigation):

```markdown
## [L1:auth] Authentication Domain
```

- Marker in heading text, not a link
- Grep-able: `grep "\[L1:auth\]"`

**Cross-references** (standard links):

```markdown
Depends on: [Database Domain](database.md)
```

- Clickable in GitHub and all renderers
- Descriptive text, clear destination

**Code references** (links with line numbers):

```markdown
Entry point: [`handle_login`](../src/auth/login.py#L42)
```

- Clickable link to exact line in GitHub
- LSP validates symbol, script extracts line number
- Code formatting makes it visually distinct

### Size Limits (enforce abstraction)

- L0: 500 lines max
- L1: 300 lines max
- L2: 200 lines max

### Directory Structure

```
docs/map/
├── MAP.md              # Entry point (format spec + index)
├── ARCHITECTURE.md     # L0: High-level overview
└── domains/            # L1: Domain docs
    ├── auth.md
    └── api.md
```

### LSP-Based Validation

- Use Pyright for Python symbol resolution
- Proper symbol discovery (classes, methods, functions)
- More reliable than grep-based matching
- Developed with TDD (tests in skill itself)

## POC Scope (Minimal)

1. **Skill scaffold**: SKILL.md with router pattern
2. **Explore workflow**: Agent reads map to understand codebase
3. **Create workflow**: Generate map for a codebase
4. **Templates**: MAP.md, L0, L1 templates
5. **Validation (Python + LSP)**: TDD-developed, Pyright-based symbol checking

## Success Criteria

- [ ] Agent can run `/code-map explore` and understand codebase structure
- [ ] Agent can run `/code-map create` to generate initial map
- [ ] Validation script catches broken references
- [ ] Templates enforce size limits and format consistency

## Ground Rules

### 1. Code is Truth, Map is Derivative

The map describes the code, not the other way around. When they conflict, the code wins. The map should be updated to reflect reality, not prescribe it.

### 2. Every Claim is Verifiable

- File links → file must exist
- Code links → symbol must exist at line (LSP)
- Descriptions → should match actual behavior
- No aspirational content ("we plan to...") - only current state

### 3. Size Limits Enforce Abstraction

If you can't describe something in N lines, you're at the wrong zoom level:

- L0 (500 lines): Can't fit? Split into more domains
- L1 (300 lines): Can't fit? Add L2 module docs
- L2 (200 lines): Can't fit? The code itself is too complex

### 4. Structure Mirrors Code

Domain boundaries in the map = domain boundaries in the code. If the map structure doesn't match the code structure, one of them needs to change.

### 5. Map is Navigable, Not Linear

Multiple entry points:

- Agents can grep for `[L1:domain]` anchors
- Humans can click links
- Both can follow references up/down the hierarchy

### 6. Stale Maps Are Worse Than No Maps

A map that lies is worse than no map at all. Validation must be:

- Automated (run on CI)
- Fast (seconds, not minutes)
- Strict (fail on any broken link)

## Use Cases

| Use Case | Actor | Flow |
|----------|-------|------|
| Cold Start | AI Agent | `/code-map explore` → read L0 → identify relevant L1 → start task |
| Task Navigation | AI Agent | User describes task → agent finds relevant domains → follows code links |
| Developer Onboarding | Human | Read MAP.md → ARCHITECTURE.md → relevant domain docs |
| Code Review | Human/AI | Check which domains a PR touches → verify understanding |
| Refactoring | Human/AI | Before changes → check "Depends On" sections → understand impact |
| Documentation Audit | AI Agent | `/code-map validate` → fix broken links → commit |

## Future Scope

### v0.2: L2 Module Docs

When L0/L1 patterns proven, add:

- `docs/map/modules/{domain}/{module}.md`
- 200 line limit per module
- Class-level and function-group documentation
- Internal patterns within a domain

### v0.3: Update Workflow

- Detect stale docs (code changed, map didn't)
- Suggest updates based on git diff
- Pre-commit hook integration

### v0.4: Multi-Language LSP

- TypeScript via tsserver
- Go via gopls
- Rust via rust-analyzer

### v0.5: Automated Generation

- AST-based initial map generation
- Human curation layer on top
- Diff-based update suggestions
