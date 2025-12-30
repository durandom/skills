# Code Map

<!-- FILL: Project name and brief one-liner -->

## Quick Start for Agents

1. Read this file for navigation overview
2. Read `ARCHITECTURE.md` for system-level context
3. Find relevant domain: `grep -r "\[L1:" domains/`
4. Dive into domain docs for code entry points
5. Follow code links to source files

**Key commands:**

```bash
# Find all L1 domains
grep -r "\[L1:" docs/map/domains/

# Find specific domain
grep -r "\[L1:domain-name\]" docs/map/

# Find all entry points in a domain
grep "^\`\[" docs/map/domains/domain-name.md
```

## Format Overview

| Level | Location | Limit | Contains |
|-------|----------|-------|----------|
| L0 | `ARCHITECTURE.md` | 500 lines | System overview, domain index |
| L1 | `domains/*.md` | 300 lines | Domain purpose, entry points, deps |
| L2 | `modules/**/*.md` | 200 lines | Module details (optional) |
| L3 | Source files | n/a | The code itself |

**Syntax:**

- Anchors: `## [L1:name] Title` (grep-able markers)
- Cross-refs: `[Text](path.md)` (standard links)
- Code refs: `` [`symbol`](file.py#L42) `` (line-specific)

See [format-spec.md](../references/format-spec.md) for full specification.

## Domains Index

| Domain | Path | Purpose |
|--------|------|---------|
<!-- FILL: Add domains as rows -->
| [domain-name] | [domains/name.md](domains/name.md) | [brief purpose] |

## Code Statistics

<!-- FILL: Update these values -->
- **Total files:** [count]
- **Languages:** [list]
- **Last updated:** [date]

## Navigation

```
┌─────────────────┐
│     MAP.md      │  ← You are here
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ARCHITECTURE.md │  ← L0: System overview
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ L1    │ │ L1    │  ← Domain docs
│domain │ │domain │
└───────┘ └───────┘
```

<!--
FILL INSTRUCTIONS:
1. Replace project name in title
2. Add all L1 domains to the Domains Index table
3. Update Code Statistics
4. Customize Quick Start commands if needed
-->
