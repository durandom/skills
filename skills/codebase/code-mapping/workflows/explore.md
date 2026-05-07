# Explore Workflow

Use this workflow to navigate an existing code map and understand a codebase.

## Prerequisites

- A code map exists at `docs/map/` (or similar location)
- You have a task or question about the codebase

## Steps

### Step 1: Locate the Map

Find the map entry point:

```bash
# Common locations
ls docs/map/README.md
ls docs/map/MAP.md
ls .map/README.md
```

If no map exists, use the **create workflow** instead.

### Step 2: Read the Entry Point

Read the map README to get:

- Project overview
- List of domains
- Link to ARCHITECTURE.md

```bash
cat docs/map/README.md
```

### Step 3: Scan Architecture (L0)

Read ARCHITECTURE.md for system overview:

```bash
cat docs/map/ARCHITECTURE.md
```

Look for:

- **System Overview** — What does this system do?
- **Domains** — What are the major subsystems?
- **Data Flow** — How does information move?
- **Cross-Cutting Concerns** — Shared infrastructure (logging, config, etc.)

### Step 4: Identify Relevant Domains

Based on your task, identify which domains are relevant.

#### Option A: Use the domains index

The README contains a table of domains. Find the one matching your task.

#### Option B: Grep for anchors

```bash
# List all L1 domains
grep -r "\[L1:" docs/map/

# Search for specific topic
grep -ri "auth" docs/map/
grep -ri "database" docs/map/
```

### Step 5: Read Domain Docs (L1)

Read the relevant domain doc:

```bash
cat docs/map/domains/auth.md
```

Look for:

- **Purpose** — What does this domain do?
- **Modules** — Links to L2 module docs
- **Depends On** — What other domains does this use?
- **Data Flow** — How data moves through the domain

### Step 6: Read Module Docs (L2)

Domain docs link to L2 module docs (not source directly):

```markdown
| Module | Purpose |
|--------|---------|
| [OAuth](modules/oauth.md) | Third-party authentication |
```

Read the relevant module doc for detailed symbol information.

### Step 7: Follow Source Links

L2 module docs contain links to actual source files with line numbers:

```markdown
| [`authorize`](../../../src/auth/oauth.py#L19) | Generate authorization URL |
```

Read the linked file at the specified line to understand the implementation.

## Quick Navigation Commands

```bash
# Find all anchors at a level
grep -r "\[L0:" docs/map/
grep -r "\[L1:" docs/map/
grep -r "\[L2:" docs/map/

# Find code links in L2 module docs
grep -E "\[\`.+\`\]\(.+#L[0-9]+\)" docs/map/modules/

# Search for a symbol across the map
grep -r "handle_login" docs/map/
```

## When to Stop

You have enough context when you can:

1. Identify which files to modify
2. Understand the data flow through those files
3. See the dependencies between components

Don't read the entire map. Read only what's relevant to your task.
