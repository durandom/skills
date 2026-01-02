# Create Workflow

Use this workflow to generate a code map for a codebase.

## Prerequisites

- Python 3.11+ available
- Source code to document (currently Python only)

## Progress Checklist

Copy this checklist and update as you work:

```
Map Creation Progress:
- [ ] Step 1: Run generator
- [ ] Step 2: Add source docstrings (L2)
- [ ] Step 3: Fill domain docs (L1)
- [ ] Step 4: Write architecture (L0)
- [ ] Step 5: Fill README
- [ ] Step 6: Validate
- [ ] Step 7: Fix errors (repeat until clean)
```

## Steps

### Step 1: Run the Generator

Generate map skeletons from source:

```bash
uv run python $SKILL_PATH/scripts/code_map.py generate <src-dir> <map-dir>
```

Example (if skill is at `.claude/skills/code-mapping`):

```bash
uv run python .claude/skills/code-mapping/scripts/code_map.py generate src/ docs/map/
```

The generator output tells you exactly what to do next:

- **Missing docstrings** — Add docstrings to source files, then re-run
- **Missing descriptions** — Edit domain/architecture docs directly
- **Orphaned files** — Source was deleted, clean up the map files

In brownfield codebases, the output is limited to 10 items per category. Fix the first batch, re-run, and repeat until clean.

### Step 2: Improve Source Docstrings (L2) — Bottom Up

Module docs are **projections** of source code—they're auto-generated from docstrings.

If a module doc has missing descriptions:

1. Open the source file (follow the `[Source]` link)
2. Add or improve the docstring in the code
3. Re-run the generator to update the markdown

Do NOT edit the module markdown directly. The source code is the single source of truth.

Stay under 200 lines per module. If exceeded, the code itself may need refactoring.

See [references/examples/l2-module.md](../references/examples/l2-module.md) for example.

### Step 3: Fill Domain Docs (L1)

For each domain doc in `docs/map/domains/`:

1. **Purpose** — What problem does this domain solve?
2. **Key Modules** — Link to L2 docs, summarize each in one line
3. **Depends On** — Cross-domain dependencies

Synthesize from L2 content. Stay under 300 lines.

See [references/examples/l1-domain.md](../references/examples/l1-domain.md) for example.
See [references/domains.md](../references/domains.md) for what domains should capture.

### Step 4: Write the Architecture (L0)

Edit `docs/map/ARCHITECTURE.md`:

1. **System Overview** — Synthesize from domain purposes
2. **Key Components** — List domains with one-line summaries
3. **Data Flow** — How do domains interact?
4. **Entry Points** — Where does execution start?

Synthesize from L1 content. Stay under 500 lines.

See [references/examples/l0-architecture.md](../references/examples/l0-architecture.md) for example.

### Step 5: Fill the README

Edit `docs/map/README.md`:

1. Add project description (one paragraph)
2. Review domains table (auto-generated)
3. Add navigation hints for common tasks

See [references/examples/readme.md](../references/examples/readme.md) for example.

### Step 6: Validate the Map

Run validation to check for errors:

```bash
uv run python $SKILL_PATH/scripts/code_map.py validate <map-dir>
```

Example (if skill is at `.claude/skills/code-mapping`):

```bash
uv run python .claude/skills/code-mapping/scripts/code_map.py validate docs/map/
```

The validator checks:

- **Structure** — Required files exist
- **File links** — All markdown links resolve
- **Code links** — Symbols exist at specified lines (AST)
- **Size limits** — Docs stay under line limits

### Step 7: Fix Validation Errors

Common fixes:

| Error | Fix |
|-------|-----|
| Missing file | Create the file or remove the link |
| Broken code link | Update line number or symbol name |
| Size limit exceeded | Split into more granular docs |

Re-run validation until all checks pass.

## Updating an Existing Map

When code changes:

1. Re-run the generator (preserves filled descriptions)
2. Review new sections and removed sections in output
3. Fill new `<!-- TODO -->` placeholders (bottom-up)
4. Run validation
5. Commit changes

## Why Bottom-Up?

The generator extracts concrete facts from code (symbols, structure). Working bottom-up means:

- **L2 (modules)**: Closest to code, easiest to describe accurately
- **L1 (domains)**: Synthesize from L2, zoom out one level
- **L0 (architecture)**: Synthesize from L1, highest abstraction

This prevents the common failure mode of writing vague architecture docs that don't match the code.
