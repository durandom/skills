---
name: code-mapping
description: Creates and navigates hierarchical code maps for AI agent and human orientation. Use when bootstrapping understanding of a codebase, creating documentation for navigation, or validating map integrity.
---

<essential_principles>

**Maps are hierarchical**: L0 (architecture) links to L1 (domains) which link to L2 (modules) which link to L3 (source code). Always start at L0 and drill down as needed.

**Anchors enable grep navigation**: Headings contain `[Lx:identifier]` markers. Find any section with `grep "\[L1:auth\]" docs/map/`.

**Size limits enforce abstraction**:

- L0: 500 lines max (system overview)
- L1: 300 lines max (domain docs)
- L2: 200 lines max (module docs)

If a doc exceeds its limit, split it into the next level down.

**Code is truth, map is derivative**: When code and map conflict, the code wins. Update the map to reflect reality.

**Bootstrap pattern**: Agents read README.md first, then ARCHITECTURE.md, then relevant domain docs based on task.

</essential_principles>

<auto_routing>

**Route based on user intent** (match first):

| User says | Action |
|-----------|--------|
| "explore", "read", "understand", "navigate", "find", "where is" | Read `workflows/explore.md`, then follow it |
| "create", "generate", "new", "build", "document", "map" | Read `workflows/create.md`, then follow it |
| "validate", "check", "verify", "lint" | Run: `uv run python $SKILL_PATH/scripts/code_map.py validate <map-dir>` |

**If intent is ambiguous**, ask:
> What would you like to do?
>
> 1. **Explore** - Navigate existing map to understand codebase
> 2. **Create** - Generate a new code map
> 3. **Validate** - Check map integrity

</auto_routing>

<quick_reference>

**Directory structure**:

```
docs/map/
├── README.md           # Entry point + domains index
├── ARCHITECTURE.md     # L0: System overview
└── domains/            # L1: Domain docs
    ├── auth.md
    └── api.md
```

**Anchor format**: `## [L1:identifier] Heading Text`

**Code link format**: `` [`symbol`](path/to/file.py#L42) ``

**Cross-reference format**: `[Domain Name](domains/name.md)`

</quick_reference>

<reference_index>

**Domain Knowledge** (`references/`):

| Reference | Purpose |
|-----------|---------|
| format-spec.md | Format rules for anchors, links, and size limits |
| examples/ | Input/output examples (l0-architecture.md, l1-domain.md, l2-module.md, readme.md) |
| domains.md | What domain docs should capture |

</reference_index>

<cli>

## Running the Scripts

The scripts use Python 3.11+ stdlib only (no external dependencies).

`$SKILL_PATH` is the base directory shown at skill load (e.g., `.claude/skills/code-mapping`).

```bash
# Validate an existing map
uv run python $SKILL_PATH/scripts/code_map.py validate <map-dir>

# Generate map skeletons from source
uv run python $SKILL_PATH/scripts/code_map.py generate <src-dir> <map-dir>
```

**Generate command features:**

- Creates one `.md` file per source file (1:1 mapping)
- Uses `<!-- TODO: description -->` placeholders
- Preserves filled descriptions on subsequent runs
- Reports new sections, removed sections, and unfilled placeholders

</cli>

<workflows_index>

**Workflows** (`workflows/`):

| Workflow | Purpose | Status |
|----------|---------|--------|
| explore.md | Navigate existing map to understand codebase | Ready |
| create.md | Generate new map for a codebase | Ready |

**Scripts** (`scripts/`):

| Script | Purpose | Status |
|--------|---------|--------|
| code_map.py | CLI entry point (validate, generate) | Ready |
| generate/ | Map skeleton generation from source | Ready |
| validate/ | Map validation (links, sizes, symbols) | Ready |

</workflows_index>

<success_criteria>
A well-executed code map:

- Has valid L0 ARCHITECTURE.md under 500 lines
- Has L1 domain docs under 300 lines each
- All file links resolve to existing files
- All code links have valid file + line number
- All anchors are unique across the map
- No orphan documents (everything linked from parent level)
</success_criteria>
