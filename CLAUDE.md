<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:

- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:

- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A collection of Claude Code skills, commands, agents, and recipes. Skills extend Claude's capabilities with specialized knowledge and workflows.

## Build & Test Commands

```bash
# Install dependencies (uses uv)
uv sync --dev

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/code_map/test_generate_snapshot.py

# Run tests matching a pattern
uv run pytest -k "test_generate"

# Update snapshots (syrupy)
uv run pytest --snapshot-update

# Lint and format
uv run ruff check --fix
uv run ruff format

# Pre-commit hooks (auto-fixes most issues)
pre-commit run --all-files
```

## Architecture

```
skills/               # Main skills (SKILL.md + references/ + workflows/ + scripts/)
├── code-mapping/     # Hierarchical codebase documentation (code maps)
├── gtd/              # GTD task management via GitHub issues
└── para/             # PARA organization with GTD synchronization

commands/             # Slash commands (.md files with YAML frontmatter)
├── commit.md         # /commit - git commit with emoji conventional commits
├── catchup.md        # /catchup - review branch changes
└── jira.md           # /jira - JIRA integration

agents/               # Subagent configurations (.md with YAML frontmatter)
└── code-map-explorer.md  # Navigate existing code maps (read-only)

recipes/              # Reusable patterns and guides
├── comments.md       # Python commenting standards (INTENT:, CRITICAL:, PERF:)
└── snapshot-testing.md

fixtures/             # Test fixtures (e.g., calculator/ for code-map tests)
tests/                # Pytest tests with syrupy snapshots
```

## Key Conventions

### Skills Structure

Each skill in `skills/` follows this pattern:

- `SKILL.md` - Main skill definition with YAML frontmatter (name, description)
- `references/` - Domain knowledge files loaded on demand
- `workflows/` - Step-by-step processes the skill can execute
- `scripts/` - Python CLI tools the skill uses

### Slash Commands

Commands in `commands/` use YAML frontmatter:

```yaml
---
description: What it does
argument-hint: [args]
allowed-tools: Read, Edit, Bash, ...
model: sonnet  # or haiku, opus
---
```

### Comment Anchors

Use keyword-prefixed comments for AI-readable anchors:

- `INTENT:` - Business goal of a code block
- `CRITICAL:` - Code that looks wrong but is right (don't refactor)
- `PERF:` - Performance optimization that sacrifices readability

### Code Maps

The code-mapping skill generates hierarchical documentation:

- L0: ARCHITECTURE.md (system overview)
- L1: domains/ (semantic groupings)
- L2: modules/ (per-file documentation)
- Anchors like `[L1:auth]` enable grep navigation

Generate/validate code maps:

```bash
python skills/code-mapping/scripts/code_map.py generate <src-dir> <map-dir>
python skills/code-mapping/scripts/code_map.py validate <map-dir>
```

### GTD CLI

Run from repo root:

```bash
./.claude/skills/gtd/scripts/gtd <command>
# Examples: capture, inbox, clarify, list, done, daily, weekly
```

## Testing

Uses pytest with syrupy for snapshot testing. Snapshots are `.ambr` files excluded from trailing-whitespace pre-commit hook.
