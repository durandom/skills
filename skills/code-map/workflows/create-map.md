# Workflow: Create Code Map

<objective>
Generate a hierarchical code map for a codebase.

Use this workflow when:

- Setting up navigation docs for a new codebase
- Formalizing understanding of an existing codebase
- Creating grep-navigable documentation for AI agents
</objective>

<required_reading>
@.claude/skills/code-map/references/format-spec.md
@.claude/skills/code-map/templates/MAP.md
@.claude/skills/code-map/templates/L0-architecture.md
@.claude/skills/code-map/templates/L1-domain.md
</required_reading>

<process>

## Step 1: Analyze Codebase

Gather basic statistics and identify the code structure:

```bash
# Count files by language
find . -type f -name "*.py" | wc -l
find . -type f -name "*.ts" -o -name "*.tsx" | wc -l
find . -type f -name "*.js" | wc -l

# Count total lines of code
find . -type f -name "*.py" -exec wc -l {} + | tail -1

# Identify entry points (common patterns)
ls -la *.py 2>/dev/null
ls -la src/*.py 2>/dev/null
ls -la cli.py main.py __main__.py 2>/dev/null
```

**Note:**

- Total file count by language
- Approximate lines of code
- Entry point files (cli, main, api)
- Directory structure depth

## Step 2: Identify Domains

Analyze the codebase to identify major functional areas:

1. **Read existing documentation** (README, CLAUDE.md, etc.)
2. **Examine directory structure** for natural groupings
3. **Look for domain patterns:**
   - CLI/API layer (commands, routes, endpoints)
   - Data layer (models, database, schema)
   - Business logic (services, handlers, transformers)
   - Infrastructure (config, utils, middleware)

**Aim for 3-10 domains.** If you identify more than 10, some can be merged or become L2 modules.

**Present to user:**

```
Proposed domains:
1. [domain-name] - [purpose]
2. [domain-name] - [purpose]
3. [domain-name] - [purpose]

Proceed with these domains? (yes / suggest changes)
```

## Step 3: Create Directory Structure

```bash
mkdir -p docs/map/domains
```

Verify the structure exists before proceeding.

## Step 4: Create MAP.md

Copy the MAP.md template and fill in:

1. **Quick Start section** - grep commands for this specific codebase
2. **Domains Index table** - list all domains with paths and purposes
3. **Code Statistics** - file counts, languages, last updated date
4. **Navigation diagram** - ASCII box showing L0 -> L1 hierarchy

Use the template at: `.claude/skills/code-map/templates/MAP.md`

## Step 5: Create ARCHITECTURE.md

Copy the L0-architecture.md template and fill in:

1. **[L0:overview] System Overview**
   - One sentence purpose
   - Primary users

2. **[L0:stack] Technology Stack**
   - Table of key technologies

3. **[L0:diagram] High-Level Architecture**
   - ASCII box diagram showing major components
   - Data flow description

4. **[L0:domains] Domain Map**
   - Links to all L1 domain docs

5. **[L0:entry-points] Entry Points**
   - Table with code links (`` [`symbol`](path#L42) ``)
   - Use actual line numbers from source files

**Size limit: 500 lines.** If larger, move details to L1 docs.

Use the template at: `.claude/skills/code-map/templates/L0-architecture.md`

## Step 6: Create L1 Domain Docs

For each domain, create `docs/map/domains/{domain-name}.md`:

1. **[L1:domain-name] Domain Name**
   - Purpose paragraph
   - In scope / out of scope boundaries

2. **Entry Points**
   - Table with code links to key classes/functions
   - Use actual line numbers

3. **Depends On**
   - Links to other domains this one depends on
   - External library dependencies

4. **Diagram** (optional)
   - ASCII box diagram of internal components

5. **Key Files**
   - Table of files with brief purposes

**Size limit: 300 lines per domain.** If larger, add L2 module docs.

Use the template at: `.claude/skills/code-map/templates/L1-domain.md`

## Step 7: Validate

Run the validation script:

```bash
uv run python .claude/skills/code-map/scripts/__main__.py docs/map
```

**Expected output:**

```
Validating docs/map...

Structure: OK
File links: OK (X checked)
Code links: OK (Y checked, AST)
Size limits: OK

All checks passed.
```

**If errors:**

1. Fix broken file links (path typos, missing files)
2. Fix code links (update line numbers, verify symbol names)
3. If size limits exceeded, split content to next level down
4. Re-run validation until all checks pass

</process>

<success_criteria>

- `docs/map/` directory exists with MAP.md, ARCHITECTURE.md, domains/
- Validation script passes with 0 errors
- All placeholders filled (no `{{placeholder}}` text)
- L0 under 500 lines, L1 files under 300 lines each
- Code links use actual line numbers from source files
- Domains cover major functional areas (3-10 domains)
</success_criteria>

<tips>

**Finding line numbers:**

```bash
# Find where a symbol is defined
grep -n "def example_function" src/module.py
grep -n "class ExampleClass" src/module.py
```

**Quick symbol validation:**
The validation script uses Python's AST to verify symbols exist at the specified lines (with a tolerance of +/- 5 lines for minor drift).

**When to add L2:**

- L1 domain doc approaches 300 lines
- Domain has multiple distinct subsystems
- Need to document internal patterns in detail

**Iterative approach:**
Start minimal. Create L0 and basic L1 docs. Add detail incrementally as you work with the codebase.

</tips>
