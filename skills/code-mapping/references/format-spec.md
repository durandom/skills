# Code Map Format Specification

Complete rules for writing and validating code maps.

## File Structure

```
docs/map/
├── README.md           # Entry point + domains index
├── ARCHITECTURE.md     # L0: System overview (≤500 lines)
└── domains/            # L1: Domain docs (≤300 lines each)
    ├── auth.md
    └── api.md
```

### README.md (Entry Point)

The map entry point provides:

1. Project name and brief description
2. Domains index table
3. Link to ARCHITECTURE.md

Template:

```markdown
# Code Map - {Project Name}

{Brief description of the project}

## Domains Index

| Domain | Path | Purpose |
|--------|------|---------|
| Auth | [domains/auth.md](domains/auth.md) | Authentication and authorization |
| API | [domains/api.md](domains/api.md) | REST API endpoints |

## Navigation

Read [ARCHITECTURE.md](ARCHITECTURE.md) for system overview.
```

### ARCHITECTURE.md (L0)

System-wide overview. Must stay under 500 lines.

Required sections:

1. **System Overview** — What the system does
2. **Key Components** — Major subsystems with links to L1 docs
3. **Data Flow** — How data moves through the system
4. **Entry Points** — Where execution starts

### Domain Docs (L1)

Each domain doc describes one subsystem. Must stay under 300 lines.

Required sections:

1. **Purpose** — What this domain does
2. **Key Files** — Important files with code links
3. **Public Interface** — Exported functions/classes
4. **Depends On** — Other domains this depends on

## Anchor Format

Anchors are markers in headings that enable grep navigation.

**Format**: `## [Lx:identifier] Heading Text`

**Rules**:

- `Lx` is the level: `L0`, `L1`, `L2`
- `identifier` is lowercase, hyphenated (e.g., `auth`, `user-management`)
- One anchor per heading
- Anchors must be unique across the entire map

**Examples**:

```markdown
## [L0:architecture] System Architecture
## [L1:auth] Authentication Domain
## [L1:api] API Domain
## [L2:oauth] OAuth Implementation
```

**Usage**:

```bash
# Find all L1 anchors
grep "\[L1:" docs/map/

# Find specific anchor
grep "\[L1:auth\]" docs/map/
```

## Code Link Format

Code links point to specific symbols in source files.

**Format**: `` [`symbol`](path/to/file.py#L42) ``

**Rules**:

- Symbol name in backticks (code formatting)
- Relative path from the markdown file
- Line number with `#L` prefix
- Symbol must exist at or near that line (±5 lines tolerance)

**Examples**:

```markdown
Entry point: [`main`](../../src/main.py#L15)
Handler: [`AuthController.login`](../../src/auth/controller.py#L42)
Config: [`DEFAULT_TIMEOUT`](../../src/config.py#L8)
```

**Validation**:

The validator uses AST parsing to verify:

1. File exists at the specified path
2. Symbol exists in the file
3. Symbol is near the specified line number

## Cross-Reference Format

Cross-references link between map documents.

**Format**: `[Display Text](relative/path.md)`

**Examples**:

```markdown
See also: [Authentication Domain](domains/auth.md)
Depends on: [Database Domain](domains/database.md)
Parent: [Architecture](../ARCHITECTURE.md)
```

## Size Limits

| Level | Max Lines | Enforcement |
|-------|-----------|-------------|
| L0 | 500 | Split into more L1 domains |
| L1 | 300 | Add L2 module docs |
| L2 | 200 | Code itself is too complex |

Size limits are checked by the validator. Exceeding a limit means you're at the wrong abstraction level.

## Content Guidelines

### What to Include

- **Architecture decisions** — Why things are structured this way
- **Entry points** — Where to start reading code
- **Key abstractions** — Important classes, functions, patterns
- **Dependencies** — What this component relies on
- **Data flow** — How information moves

### What to Exclude

- **Implementation details** — Let the code speak for itself
- **API documentation** — That belongs in docstrings
- **Tutorials** — Maps are for navigation, not teaching
- **Aspirational content** — Only document current state

### Writing Style

- **Terse over verbose** — Every line must earn its place
- **Links over descriptions** — Point to code, don't paraphrase it
- **Structure over prose** — Tables and lists over paragraphs
- **Current over historical** — No "we used to..." or "we plan to..."
