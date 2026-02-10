# Agent Instructions

Claude Code skills, commands, agents, and recipes. Skills extend Claude's capabilities with specialized knowledge and workflows.

## Build & Test

```bash
uv sync --dev                    # Install deps
uv run pytest                    # All tests
uv run pytest --snapshot-update  # Update syrupy snapshots
uv run ruff check --fix && uv run ruff format  # Lint + format
pre-commit run --all-files       # Pre-commit hooks
```

## Architecture

```
skills/               # SKILL.md + references/ + scripts/
├── code-mapping/     # Hierarchical codebase documentation
├── gtd/              # GTD task management
├── para/             # PARA organization
└── recipes/          # Reusable development patterns

commands/             # Slash commands (.md with YAML frontmatter)
agents/               # Subagent configurations (.md with YAML frontmatter)
fixtures/             # Test fixtures
tests/                # Pytest + syrupy snapshots (.ambr files)
```

## Versioning

Version is tracked in three places — `.claude-plugin/plugin.json` is the source of truth:

- `.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `metadata.version` AND `plugins[0].version`
- `pyproject.toml` → `version`

All three MUST stay in sync. When bumping, update all files.

## Session Completion

Work is NOT complete until `git push` succeeds.

1. File issues for remaining work
2. Run quality gates if code changed (tests, linters)
3. Update issue status (close finished, update in-progress)
4. Push:

   ```bash
   git pull --rebase && bd sync && git push
   git status  # MUST show "up to date with origin"
   ```

5. Hand off context for next session
