---
name: recipes
description: Reusable development patterns and guides for AI-assisted workflows. Use when asking about CLI design for agents, CLI location, config discovery, vault, commenting standards, snapshot testing, credential storage, Python project architecture, semantic zoom, skill writing, Claude tools, agent teams, extracting deterministic work, or plugin authoring and distribution.
---

<essential_principles>

## What Recipes Are

Recipes are **standalone reference documents** -- each captures a proven pattern or practice for AI-assisted development. They are not step-by-step procedures; they are knowledge you read and apply.

**Three categories:**

| Category | Recipes | When to Use |
|----------|---------|-------------|
| **AI Agent Patterns** | semantic-zoom, agentic-cli, extract-deterministic | Designing AI interactions or CLI tools for agents |
| **Development Practices** | comments, agent-skills, claude-tools, snapshot-testing | Writing code, skills, or tests in this ecosystem |
| **Distribution** | claude-plugin-authoring | Packaging skills as installable Claude Code plugins |
| **Architecture & Implementation** | python-project-architecture, keyring-credential-storage, cli-location-discovery | Structuring Python projects, handling credentials, or CLI location/config discovery |

</essential_principles>

<intake>
What pattern or practice do you need guidance on?

1. **AI agent CLI design** - Safe-by-default CLI patterns for agentic workflows
2. **Extracting deterministic work** - When to script vs. when to prompt
3. **Semantic zoom** - Controlling abstraction level in AI interactions
4. **Python commenting standards** - INTENT:, CRITICAL:, PERF: anchors
5. **Writing Claude Code skills** - Skill authoring patterns and best practices
6. **Claude Code tools reference** - All 20 native tools, coordination patterns, agent spawning
7. **Snapshot testing** - Approval testing with syrupy
8. **Python project architecture** - Project structure for CLI tools
9. **Keyring credential storage** - Secure credential management patterns
10. **Claude plugin authoring** - Packaging skills as installable plugins
11. **CLI location & config discovery** - Finding scripts and config from arbitrary cwd

**Wait for response before proceeding.**
</intake>

<routing>

| Response | Reference |
|----------|-----------|
| 1, "cli", "agentic", "safe", "flags", "non-interactive" | `references/agentic-cli.md` |
| 2, "deterministic", "extract", "script vs prompt" | `references/extract-deterministic.md` |
| 3, "zoom", "abstraction", "detail level", "semantic" | `references/semantic-zoom.md` |
| 4, "comment", "intent", "critical", "perf", "anchor" | `references/comments.md` |
| 5, "skill", "writing", "skill.md", "author" | `references/agent-skills.md` |
| 6, "tools", "task tool", "claude tools", "subagent", "task management" | `references/claude-tools.md` |
| 7, "snapshot", "testing", "syrupy", "approval" | `references/snapshot-testing.md` |
| 8, "architecture", "python project", "cli tool", "structure" | `references/python-project-architecture.md` |
| 9, "keyring", "credential", "password", "secret" | `references/keyring-credential-storage.md` |
| 10, "plugin", "marketplace", "distribute", "package", "install" | `references/claude-plugin-authoring.md` |
| 11, "location", "discovery", "vault", "find_vault", "cwd", "wrong directory", "config init", "bootstrap" | `references/cli-location-discovery.md` |
| Other | Clarify intent, then select appropriate reference |

**After identifying the reference, read it and apply its guidance to the user's situation.**

</routing>

<reference_index>

## AI Agent Patterns

- [agentic-cli.md](references/agentic-cli.md) - CLI design patterns for AI agents (non-interactive, capability gradient, dry-run)
- [extract-deterministic.md](references/extract-deterministic.md) - When to extract deterministic work from AI workflows into scripts
- [semantic-zoom.md](references/semantic-zoom.md) - Controlling abstraction level in AI interactions

## Development Practices

- [comments.md](references/comments.md) - Python commenting standards with INTENT:, CRITICAL:, PERF: anchors
- [agent-skills.md](references/agent-skills.md) - Patterns for writing effective Claude Code skills
- [claude-tools.md](references/claude-tools.md) - Complete Claude Code tools reference (all 20 native tools)
- [snapshot-testing.md](references/snapshot-testing.md) - Approval testing with syrupy framework

## Distribution

- [claude-plugin-authoring.md](references/claude-plugin-authoring.md) - Packaging skills as installable Claude Code plugins

## Architecture & Implementation

- [python-project-architecture.md](references/python-project-architecture.md) - Python project architecture for CLI tools
- [keyring-credential-storage.md](references/keyring-credential-storage.md) - Keyring credential storage pattern
- [cli-location-discovery.md](references/cli-location-discovery.md) - CLI location & config discovery for skill-bundled scripts

</reference_index>

<success_criteria>

- User gets directed to the right reference for their question
- Reference content is applied to the user's specific situation, not just recited
- Multiple references can be combined when a question spans categories

</success_criteria>
