# Create Workflow

Use this workflow to generate a code map for a codebase.

## Prerequisites

- Python 3.11+ available
- Source code to document (currently Python only)

## Steps

### Step 1: Run the Generator

Generate map skeletons from source:

```bash
uv run python <skill-path>/scripts/code_map.py generate <src-dir> <map-dir>
```

Example:

```bash
uv run python .claude/skills/code-mapping/scripts/code_map.py generate src/ docs/map/
```

The generator:

- Creates L2 module docs with symbols extracted via AST
- Creates L1 domain docs linking to modules
- Adds `<!-- TODO: description -->` placeholders
- Preserves existing descriptions on subsequent runs

### Step 2: Review Generated Structure

Check what was created:

```bash
ls -la docs/map/
ls -la docs/map/domains/
ls -la docs/map/modules/
```

Expected structure:

```
docs/map/
├── README.md           # Entry point (needs project description)
├── ARCHITECTURE.md     # L0 skeleton (needs overview)
├── domains/            # L1 docs (need descriptions)
│   └── {domain}.md
└── modules/            # L2 docs (symbols extracted, need context)
    └── {domain}/
        └── {module}.md
```

### Step 3: Fill Module Docs (L2) — Bottom Up

For each module doc in `docs/map/modules/`:

1. Replace `<!-- TODO: description -->` placeholders
2. Explain *why* each symbol exists (not what it does)
3. Note any non-obvious patterns or decisions

Stay under 200 lines per module. These are closest to code—be precise.

### Step 4: Fill Domain Docs (L1)

For each domain doc in `docs/map/domains/`:

1. **Purpose** — What problem does this domain solve?
2. **Key Modules** — Link to L2 docs, summarize each in one line
3. **Depends On** — Cross-domain dependencies

Synthesize from L2 content. Stay under 300 lines.

### Step 5: Write the Architecture (L0)

Edit `docs/map/ARCHITECTURE.md`:

1. **System Overview** — Synthesize from domain purposes
2. **Key Components** — List domains with one-line summaries
3. **Data Flow** — How do domains interact?
4. **Entry Points** — Where does execution start?

Synthesize from L1 content. Stay under 500 lines.

### Step 6: Fill the README

Edit `docs/map/README.md`:

1. Add project description (one paragraph)
2. Review domains table (auto-generated)
3. Add navigation hints for common tasks

### Step 7: Validate the Map

Run validation to check for errors:

```bash
uv run python <skill-path>/scripts/code_map.py validate <map-dir>
```

Example:

```bash
uv run python .claude/skills/code-mapping/scripts/code_map.py validate docs/map/
```

The validator checks:

- **Structure** — Required files exist
- **File links** — All markdown links resolve
- **Code links** — Symbols exist at specified lines (AST)
- **Size limits** — Docs stay under line limits

### Step 8: Fix Validation Errors

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
