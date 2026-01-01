# Code Mapping

**Hierarchical documentation that helps AI agents and humans navigate codebases.**

## The Problem

AI agents start every session with zero memory. They waste significant context—and time—just answering "where am I?" before doing useful work. Even with CLAUDE.md, agents lack a systematic way to navigate codebases at different abstraction levels.

Humans face the same challenge. Onboarding to a new codebase means reading random files until patterns emerge. Architecture docs exist but rarely connect to actual code locations.

## The Solution

**Code maps** provide hierarchical documentation with four zoom levels:

| Level | Scope | Max Lines | Example |
|-------|-------|-----------|---------|
| L0 | System architecture | 500 | `ARCHITECTURE.md` |
| L1 | Domains/subsystems | 300 | `domains/auth.md` |
| L2 | Modules/components | 200 | `modules/auth/oauth.md` |
| L3 | Source code | — | Actual `.py`, `.ts` files |

**Key features:**

- **Anchors enable grep navigation**: Headings contain `[Lx:identifier]` markers. Find any section with `grep "[L1:auth]" docs/map/`.
- **Size limits enforce abstraction**: Can't fit in N lines? You're at the wrong zoom level. Split down.
- **Code links are verifiable**: Links include line numbers, validated by AST parsing.

## What This Skill Does

| Operation | Command | Purpose |
|-----------|---------|---------|
| **Explore** | Read existing map | Orient in codebase, find relevant domains |
| **Generate** | `code_map.py generate <src> <map>` | Create map skeletons from source AST |
| **Validate** | `code_map.py validate <map>` | Check links, sizes, anchors |

## The Commenting Philosophy

Code maps and code comments serve the same purpose at different scales:

| Scale | Mechanism | Purpose |
|-------|-----------|---------|
| **Architecture** | Map anchors (`[L1:auth]`) | Navigate between domains |
| **Implementation** | Comment anchors (`INTENT:`, `CRITICAL:`) | Preserve decisions within code |

Both are **prompts for the next agent**. They explain *intent* and *architecture*, not syntax.

### Comment Anchor Patterns

Use these keywords in code comments to create navigation points:

- `INTENT:` — Business goal of a code block
- `CRITICAL:` — Code that looks wrong but is right (don't refactor)
- `PERF:` — Performance optimization that sacrifices readability

```python
# INTENT: Custom retry loop because tenacity conflicts with our Celery version.
# CRITICAL: Do not refactor to use a decorator.
for i in range(3):
    ...
```

These comments become searchable anchors, just like map headings.

## Ground Rules

### 1. Code is Truth, Map is Derivative

The map describes the code, not the other way around. When they conflict, the code wins.

### 2. Every Claim is Verifiable

- File links → file must exist
- Code links → symbol must exist at line (AST-validated)
- No aspirational content ("we plan to...") — only current state

### 3. Size Limits Enforce Abstraction

If you can't describe something in N lines, split to the next level down:

- L0 (500 lines): Split into more domains
- L1 (300 lines): Add L2 module docs
- L2 (200 lines): The code itself is too complex

### 4. Structure Mirrors Code

Domain boundaries in the map = domain boundaries in the code.

### 5. Stale Maps Are Worse Than No Maps

A map that lies is worse than no map. Validation must be automated, fast, and strict.

## Use Cases

| Use Case | Actor | Flow |
|----------|-------|------|
| Cold Start | AI Agent | Explore → read L0 → identify relevant L1 → start task |
| Task Navigation | AI Agent | User describes task → find relevant domains → follow code links |
| Developer Onboarding | Human | Read README → ARCHITECTURE → relevant domain docs |
| Code Review | Human/AI | Check which domains a PR touches → verify understanding |
| Refactoring | Human/AI | Check "Depends On" sections → understand impact |
| Documentation Audit | AI Agent | Validate → fix broken links → commit |

## Directory Structure

```
docs/map/
├── README.md           # Entry point + domains index
├── ARCHITECTURE.md     # L0: System overview
├── domains/            # L1: Domain docs
│   ├── auth.md
│   └── api.md
└── modules/            # L2: Module docs (per-file or component)
    ├── auth/
    │   └── oauth.md
    └── api/
        └── endpoints.md
```
