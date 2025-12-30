# Code Map Format Specification

This document defines the standard format for hierarchical code maps.

## Overview

Code maps provide navigable documentation at different abstraction levels:

- **L0**: System-wide architecture (one file)
- **L1**: Domain/subsystem documentation (multiple files)
- **L2**: Module/component documentation (many files)
- **L3**: Source code itself (no map docs needed)

## Zoom Levels

### L0: ARCHITECTURE.md

The single entry point for understanding the entire system.

**Location**: `docs/map/ARCHITECTURE.md`
**Size limit**: 500 lines
**Contains**:

- System purpose and boundaries
- High-level component diagram (ASCII or mermaid)
- Domain overview with links to L1 docs
- Key data flows
- Critical dependencies

**Example header**:

```markdown
## [L0:overview] System Overview

This system converts Foundry VTT modules to Obsidian vaults.

## [L0:domains] Domains

- [Extraction](domains/extraction.md) - Module unpacking
- [Conversion](domains/conversion.md) - Content transformation
- [Rendering](domains/rendering.md) - Output generation
```

### L1: Domain Documentation

Each major subsystem gets its own file in `domains/`.

**Location**: `docs/map/domains/{domain-name}.md`
**Size limit**: 300 lines
**Contains**:

- Domain purpose and boundaries
- Key concepts and terminology
- Module overview with code links
- Dependencies on other domains
- Entry points and data flow

**Example**:

```markdown
## [L1:extraction] Extraction Domain

Handles unpacking Foundry VTT modules from LevelDB to JSON.

### Key Concepts
- **Compendium Pack**: A LevelDB database containing documents
- **Document Types**: Items, Actors, JournalEntries, RollTables

### Entry Points
- [`FoundryExtractor`](../../src/fvtt2obsidian/extractor.py#L15)
- [`extract_pack()`](../../src/fvtt2obsidian/extractor.py#L42)

### Depends On
- [Models Domain](models.md) for document types
```

### L2: Module Documentation

For complex domains, break down into module-level docs.

**Location**: `docs/map/modules/{domain}/{module}.md`
**Size limit**: 200 lines
**Contains**:

- Module purpose
- Class/function inventory with code links
- Internal patterns
- Interface boundaries

**When to use L2**:

- Domain doc exceeds 300 lines
- Module has 5+ significant classes/functions
- Complex internal patterns need explanation

### L3: Source Code

The actual implementation. No map documentation at this level.

**Purpose**: L3 is always the source of truth. Maps describe L3, not prescribe it.

## Anchors

Anchors are markers in headings that enable grep-based navigation.

**Format**: `## [Lx:identifier] Title`

**Rules**:

- Always in square brackets
- Level prefix: `L0:`, `L1:`, or `L2:`
- Identifier: lowercase, hyphens, alphanumeric only
- Placed at start of heading text

**Examples**:

```markdown
## [L0:overview] System Overview
## [L1:auth] Authentication Domain
## [L2:jwt] JWT Token Handling
```

**Navigation via grep**:

```bash
# Find auth domain section
grep -r "\[L1:auth\]" docs/map/

# Find all L1 anchors
grep -r "\[L1:" docs/map/

# Find specific module
grep -r "\[L2:jwt\]" docs/map/
```

**Why anchors, not IDs**: Standard markdown IDs are auto-generated from headings and vary by renderer. Explicit anchors in the text are portable and grep-able.

## Cross-References

Links between map documents use standard markdown syntax.

**Format**: `[Descriptive Text](relative/path.md)`

**Examples**:

```markdown
# From ARCHITECTURE.md
See [Extraction Domain](domains/extraction.md) for module unpacking.

# From a domain doc
Depends on [Models Domain](models.md) for document types.

# From a module doc to parent domain
Part of [Extraction Domain](../extraction.md).
```

**Rules**:

- Always use relative paths from current file
- Descriptive text should explain what's at the destination
- Must resolve to existing files (validated)

## Code References

Links to source code use backtick formatting with line numbers.

**Format**: `` [`symbol`](path/to/file.ext#L42) ``

**Components**:

- Backticks around symbol name (distinguishes from prose links)
- Relative path to source file
- `#L42` anchor for line number

**Examples**:

```markdown
Entry point: [`FoundryExtractor`](../../src/fvtt2obsidian/extractor.py#L15)
Main method: [`extract_pack()`](../../src/fvtt2obsidian/extractor.py#L42)
Helper: [`_parse_document`](../../src/fvtt2obsidian/extractor.py#L87)
```

**Validation**:

1. File at path must exist
2. Line number must be valid
3. Symbol should exist at or near that line (LSP check)

**Why line numbers**: GitHub renders these as direct links to the line. Agents can jump directly to relevant code.

**Maintenance**: When code changes, line numbers may drift. Validation catches broken references.

## Size Limits

Size limits enforce appropriate abstraction at each level.

| Level | Limit | If Exceeded |
|-------|-------|-------------|
| L0 | 500 lines | Split into more L1 domains |
| L1 | 300 lines | Add L2 module docs |
| L2 | 200 lines | Simplify or split module |

**Why limits matter**:

- Forces decisions about what's essential
- Prevents documentation bloat
- Keeps each level scannable
- Maintains hierarchical navigation value

**Checking limits**:

```bash
wc -l docs/map/ARCHITECTURE.md          # Should be <= 500
wc -l docs/map/domains/*.md | sort -n   # Each <= 300
wc -l docs/map/modules/**/*.md | sort -n # Each <= 200
```

## Directory Structure

Standard layout for a code map:

```
docs/map/
├── MAP.md              # Entry point (format explanation + index)
├── ARCHITECTURE.md     # L0: System-wide overview
├── domains/            # L1: Domain documentation
│   ├── extraction.md
│   ├── conversion.md
│   └── rendering.md
└── modules/            # L2: Module documentation (optional)
    ├── extraction/
    │   ├── cache.md
    │   └── parser.md
    └── conversion/
        └── linker.md
```

**MAP.md contents**:

- Brief explanation of the map format
- How to navigate (for humans and agents)
- Index of all L1 domains
- Link to ARCHITECTURE.md for system overview

## Validation Rules

All code maps must pass these validations:

### 1. File Links Resolve

Every `[text](path.md)` must point to an existing file.

```bash
# Extract all markdown links, check each exists
grep -oP '\[.*?\]\(\K[^)]+(?=\))' docs/map/*.md | while read link; do
  test -f "docs/map/$link" || echo "Missing: $link"
done
```

### 2. Code Links Resolve

Every `` [`symbol`](file#L42) `` must have valid file and line.

**Basic check** (file + line exists):

```bash
# Parse code links, verify file and line number
```

**LSP check** (symbol at line):

- Use Pyright/tsserver to verify symbol exists at specified location
- Catches renamed/moved symbols

### 3. Size Limits Met

No file exceeds its level's limit.

### 4. Anchors Are Unique

Each `[Lx:identifier]` appears exactly once across all files.

### 5. No Orphan Files

Every L1 domain is linked from ARCHITECTURE.md.
Every L2 module is linked from its parent L1 domain.

## Best Practices

### Writing L0 (ARCHITECTURE.md)

- Start with "what is this system for?"
- Use ASCII diagrams for component relationships
- Link to ALL L1 domains
- Keep domain descriptions to 2-3 sentences each
- Include one "quick start" code path for orientation

### Writing L1 (Domain Docs)

- Start with domain boundaries: what's IN, what's OUT
- Define domain-specific terminology
- List entry points with code links
- Document dependencies on other domains
- Include common usage patterns

### Writing L2 (Module Docs)

- Start with "why this module exists separately"
- Document public interface fully
- Note internal patterns/conventions
- Explain non-obvious design decisions
- Keep implementation details minimal

### Maintaining Maps

- Update map when code changes significantly
- Run validation on CI
- Treat broken links as build failures
- Prefer small incremental updates over large rewrites
