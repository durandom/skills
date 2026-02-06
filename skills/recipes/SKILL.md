---
name: recipes
description: Reusable development patterns and guides for AI-assisted workflows. Use when asking about CLI design for agents, commenting standards, snapshot testing, credential storage, Python project architecture, semantic zoom, skill writing, Claude tools, or extracting deterministic work.
---

<essential_principles>

## What Recipes Are

Recipes are **standalone reference documents** -- each captures a proven pattern or practice for AI-assisted development. They are not step-by-step procedures; they are knowledge you read and apply.

**Three categories:**

| Category | Recipes | When to Use |
|----------|---------|-------------|
| **AI Agent Patterns** | semantic-zoom, agentic-cli, extract-deterministic | Designing AI interactions or CLI tools for agents |
| **Development Practices** | comments, writing-skills, claude-tools, snapshot-testing | Writing code, skills, or tests in this ecosystem |
| **Architecture** | python-project-architecture, keyring-credential-storage | Structuring Python projects or handling credentials |

</essential_principles>

<intake>
What pattern or practice do you need guidance on?

1. **AI agent CLI design** - Safe-by-default CLI patterns for agentic workflows
2. **Extracting deterministic work** - When to script vs. when to prompt
3. **Semantic zoom** - Controlling abstraction level in AI interactions
4. **Python commenting standards** - INTENT:, CRITICAL:, PERF: anchors
5. **Writing Claude Code skills** - Skill authoring patterns and best practices
6. **Claude Code tools reference** - Task tool, subagents, tool usage
7. **Snapshot testing** - Approval testing with syrupy
8. **Python project architecture** - Project structure for CLI tools
9. **Keyring credential storage** - Secure credential management patterns

**Wait for response before proceeding.**
</intake>

<routing>

| Response | Reference |
|----------|-----------|
| 1, "cli", "agentic", "safe", "flags", "non-interactive" | `references/agentic-cli.md` |
| 2, "deterministic", "extract", "script vs prompt" | `references/extract-deterministic.md` |
| 3, "zoom", "abstraction", "detail level", "semantic" | `references/semantic-zoom.md` |
| 4, "comment", "intent", "critical", "perf", "anchor" | `references/comments.md` |
| 5, "skill", "writing", "skill.md", "author" | `references/writing-skills.md` |
| 6, "tools", "task tool", "subagent", "claude tools" | `references/claude-tools.md` |
| 7, "snapshot", "testing", "syrupy", "approval" | `references/snapshot-testing.md` |
| 8, "architecture", "python project", "cli tool", "structure" | `references/python-project-architecture.md` |
| 9, "keyring", "credential", "password", "secret" | `references/keyring-credential-storage.md` |
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
- [writing-skills.md](references/writing-skills.md) - Patterns for writing effective Claude Code skills
- [claude-tools.md](references/claude-tools.md) - Claude Code Task management tools reference
- [snapshot-testing.md](references/snapshot-testing.md) - Approval testing with syrupy framework

## Architecture & Implementation

- [python-project-architecture.md](references/python-project-architecture.md) - Python project architecture for CLI tools
- [keyring-credential-storage.md](references/keyring-credential-storage.md) - Keyring credential storage pattern

</reference_index>

<success_criteria>

- User gets directed to the right reference for their question
- Reference content is applied to the user's specific situation, not just recited
- Multiple references can be combined when a question spans categories

</success_criteria>
