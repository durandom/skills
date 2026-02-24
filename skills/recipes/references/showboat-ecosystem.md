# Recipe: Showboat Ecosystem — Agent-Driven Documentation

**Target Audience:** AI Coding Agents and their supervisors
**Goal:** Understand when and why to use Showboat, Rodney, and Chartroom — and how to build project documentation that grows with the code.

---

## The Problem

> "The job of a software engineer isn't to write code, it's to deliver code that works."
> — Simon Willison

Automated tests prove correctness to machines. But supervisors need **visible proof** — screenshots, command output, charts — that demonstrate the software actually works. Traditional docs are written once, then rot.

## The Toolkit

Three CLI tools, designed to be operated by AI agents. Each is self-documenting via `--help`.

| Tool | Purpose | Discovers via |
|------|---------|---------------|
| **Showboat** | Build Markdown demo documents (text, command output, images) | `showboat --help` |
| **Rodney** | Browser automation — navigate, click, screenshot web UIs | `rodney --help` |
| **Chartroom** | Generate charts from CSV/TSV/JSON/SQL data | `chartroom --help` |

### Design Philosophy

These tools are **not designed for humans** — they are designed for agents to read `--help` and operate independently. This means:

- **Do NOT include CLI references in prompts.** They will go stale. Instead, tell the agent the tool exists and let it run `--help` itself.
- **Do NOT memorize flags.** The `--help` text is the single source of truth and is written to be parseable by agents.
- **Each tool stands alone.** They compose via loose conventions (image paths, stdout), not tight coupling.

### What Each Tool Can Do

**Showboat** — the document builder:

- Initialize a new document with a title
- Add narrative text (notes, explanations)
- Execute commands and capture their output into the document
- Embed images (from Chartroom, Rodney, or any file path)
- Stream documents to a remote Datasette instance in real-time via `SHOWBOAT_REMOTE_URL`

**Rodney** — the browser driver:

- Start/stop a headless Chrome session
- Navigate to URLs, click elements, execute JavaScript
- Take screenshots at any point
- Designed for capturing web UI interactions as proof-of-work

**Chartroom** — the chart generator:

- Turn tabular data (CSV, TSV, JSON, SQL) into PNG charts
- Supports bar, line, scatter, histogram
- Auto-generates accessibility-compliant alt text
- Outputs as raw image, markdown+alt, or plain alt text

### Composition Pattern

```
Data source → Chartroom → chart.png ─┐
                                      ├─→ Showboat document
CLI commands → showboat exec ─────────┤
                                      │
Web UI → Rodney screenshots ──────────┘
```

The tools compose through the filesystem: any tool that produces an image path can feed into `showboat image`. Any command output feeds into `showboat exec`.

---

## Pattern: Living Documentation with Showboat

This pattern formalizes how to use Showboat to create project documentation that **stays current** as the project evolves.

### The Problem with One-Shot Docs

Most generated docs have a half-life of weeks. The code changes, the docs don't, and soon they're misleading. The fix: **make the documentation a script that re-runs.**

### Architecture

```
project/
├── docs/
│   ├── showboat/              # Generated output (gitignored or committed)
│   │   ├── overview.md
│   │   ├── api-demo.md
│   │   └── images/
│   └── showboat-scripts/      # The scripts that PRODUCE the docs
│       ├── overview.sh
│       ├── api-demo.sh
│       └── README.md          # Index: what each script demonstrates
```

**Key insight:** The scripts are the source of truth, not the generated Markdown. Commit both, but the scripts are what you maintain.

### Script Anatomy

A showboat script is a shell script that orchestrates a demo. Keep it **deliberately open-ended** — describe the intent, not the exact output.

```bash
#!/usr/bin/env bash
# showboat-scripts/api-demo.sh
# INTENT: Demonstrate the API's core CRUD operations work end-to-end.
# AUDIENCE: New developers, code reviewers, project supervisors.
# REFRESH: Run after any API route changes.

set -euo pipefail

showboat init "API Demo — $(date +%Y-%m-%d)"

showboat note "## Setup"
showboat note "Start the dev server and verify it responds."
showboat exec "curl -s http://localhost:8080/health | jq ."

showboat note "## Create a Resource"
showboat exec "curl -s -X POST http://localhost:8080/items -d '{\"name\": \"test\"}' | jq ."

showboat note "## List Resources"
showboat exec "curl -s http://localhost:8080/items | jq ."

showboat note "## Cleanup"
showboat exec "curl -s -X DELETE http://localhost:8080/items/1"

# If the project has a web UI, use Rodney for visual proof:
# rodney start
# rodney open http://localhost:8080
# rodney screenshot /tmp/dashboard.png
# showboat image /tmp/dashboard.png
# rodney stop
```

### The Subagent Pattern

For richer documentation, delegate script execution to a subagent. The main agent (or a human) writes the script; a subagent runs it with Showboat.

**Why a subagent?**

- Protects the main context window from verbose output
- The subagent can adapt if commands fail (retry, adjust, explain)
- Multiple showboat scripts can run in parallel as separate subagents

**Prompt pattern for the subagent:**

```
You are a documentation agent. Your job is to run a showboat script
and produce a polished demo document.

Script: {path to showboat script}

Rules:
1. Run `showboat --help` first to learn the commands.
2. Execute the script step by step. If a step fails, add a note
   explaining what happened and continue.
3. Add context between steps — explain WHY, not just WHAT.
4. If the script uses Rodney or Chartroom, run their --help too.
5. The output document should be understandable by someone who
   has never seen this project before.
```

### Keeping Docs Current

| Trigger | Action |
|---------|--------|
| **CI pipeline** | Run showboat scripts as a post-test step. Commit updated docs or publish to Datasette. |
| **PR review** | Reviewer checks if showboat scripts need updates for changed functionality. |
| **Release** | Re-run all showboat scripts to produce current release docs. |
| **New feature** | Author writes a new showboat script alongside the feature code. |

### Cross-Project Consistency

To get similar documentation structure across projects, standardize the **script headers** and **document sections**, not the Showboat commands.

**Standard script header:**

```bash
# INTENT: One sentence — what this document proves.
# AUDIENCE: Who reads this (devs, reviewers, ops, users).
# REFRESH: When to re-run (after API changes, on release, etc.).
# PREREQS: What must be running (server, database, etc.).
```

**Standard document sections:**

| Section | Purpose |
|---------|---------|
| **Setup** | Environment, prerequisites, health checks |
| **Core Demo** | The main functionality being documented |
| **Edge Cases** | Error handling, boundary conditions (optional) |
| **Visual Proof** | Screenshots via Rodney, charts via Chartroom (optional) |
| **Teardown** | Cleanup steps |

### Anti-Patterns

| Don't | Why | Do Instead |
|-------|-----|------------|
| Hardcode expected output in scripts | Breaks when behavior changes | Let `showboat exec` capture actual output |
| Write showboat commands directly in SKILL.md | Goes stale, duplicates `--help` | Tell agent the tool exists, let it `--help` |
| Generate docs once and forget | Half-life of weeks | Make scripts re-runnable, trigger in CI |
| Put all demos in one giant script | Slow, hard to maintain, context-blowout for subagents | One script per logical feature area |
| Skip the INTENT header | Agent/human doesn't know when to re-run | Always document intent and refresh trigger |

---

## Quick Start for Agents

When asked to create documentation with Showboat:

1. **Discover:** Run `showboat --help` (and `rodney --help` / `chartroom --help` if needed)
2. **Plan:** Decide what to demonstrate — focus on proof-of-work, not code walkthrough
3. **Script:** Write a shell script with INTENT/AUDIENCE/REFRESH headers
4. **Execute:** Run the script (or hand it to a subagent)
5. **Review:** Read the generated Markdown — does it tell a coherent story?

When asked to update existing documentation:

1. Check `docs/showboat-scripts/` for existing scripts
2. Identify which scripts are affected by the code changes
3. Re-run those scripts
4. Verify the output still tells a coherent story
