---
name: code-map
description: Create and navigate hierarchical code maps for AI agent orientation. Use when bootstrapping understanding of a codebase, creating documentation for agent navigation, or validating map integrity.
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

**Bootstrap pattern**: Agents read MAP.md first, then ARCHITECTURE.md, then relevant domain docs based on task.

</essential_principles>

<intake>
What would you like to do?

1. **Explore** - Read existing map to understand a codebase
2. **Create** - Generate a code map for a codebase
3. **Validate** - Check map integrity (links, sizes, anchors)

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "explore", "read", "understand", "navigate" | `workflows/explore.md` |
| 2, "create", "generate", "new", "build" | `workflows/create-map.md` |
| 3, "validate", "check", "verify", "lint" | Run validation script (see below) |

**For validation (option 3):**

```bash
uv run python .claude/skills/code-map/scripts/__main__.py <map-dir>
# Example:
uv run python .claude/skills/code-map/scripts/__main__.py docs/map
```

**After reading the workflow, follow it exactly.**
</routing>

<quick_reference>

**Directory structure**:

```
docs/map/
├── MAP.md              # Entry point
├── ARCHITECTURE.md     # L0: System overview
└── domains/            # L1: Domain docs
    ├── domain-a.md
    └── domain-b.md
```

**Anchor format**: `## [L1:identifier] Heading Text`

**Code link format**: `` [`symbol`](path/to/file.py#L42) ``

**Cross-reference format**: `[Domain Name](domains/name.md)`

</quick_reference>

<reference_index>

**Domain Knowledge** (`references/`):

| Reference | Purpose |
|-----------|---------|
| format-spec.md | Complete format specification with all rules and examples |

</reference_index>

<workflows_index>

**Workflows** (`workflows/`):

| Workflow | Purpose | Status |
|----------|---------|--------|
| explore.md | Navigate existing map to understand codebase | Ready |
| create-map.md | Generate new map for a codebase | Ready |

**Scripts** (`scripts/`):

| Script | Purpose | Status |
|--------|---------|--------|
| lsp_client.py | Python AST-based symbol validation | Ready |
| validate_map.py | Check links, sizes, anchors | Ready |
| **main**.py | CLI entry point for validation | Ready |

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
