## Why

The original Layton vision was too ambitious — spanning GTD, Calendar, Jira, Email, and Slack integration all at once. This stage establishes the foundation: a minimal CLI that verifies Beads integration and provides temporal context, before adding skill aggregation or AI synthesis.

Stage 0 proves the core architecture works: Beads as the "notepad" (state management), `.layton/` as the "filing cabinet" (config/preferences), and a thin CLI for deterministic operations.

## What Changes

- **New skill**: `skills/layton/` with minimal CLI and SKILL.md scaffold
- **New CLI commands**:
  - `layton doctor` - Health check verifying Beads availability and config validity
  - `layton context` - Temporal context (time of day, work hours, timezone)
  - `layton config` - Personal configuration management (show/set/init)
- **New config directory**: `.layton/` for per-repo settings
- **Beads conventions**: Define how Layton uses Beads tags (`watching`, `focus`, etc.)

## Capabilities

### New Capabilities

- `cli-framework`: Global CLI behavior (no-arg defaults, `--json`/`--verbose` flags, output format consistency, exit codes)
- `cli-doctor`: Health check command verifying Beads availability and config validity, with hidden `--fix` flag
- `cli-context`: Temporal context command (time-of-day classification, work hours calculation)
- `cli-config`: Personal configuration as key-value store (init/show/keys/get/set commands)
- `beads-conventions`: How Layton uses Beads for state management (labels: `watching`, `focus`, `layton`)

### Modified Capabilities

(None - this is greenfield)

## Impact

- **New files**: `skills/layton/` directory structure with CLI and SKILL.md
- **Dependencies**: Requires `bd` CLI (Beads) to be installed
- **Config files**: Creates `.layton/config.json` per-repo (gitignore-able)
- **No breaking changes**: This is additive

## References

- **[.planning/layton.md](../../../.planning/layton.md)** - Exploration session summary with architecture decisions, the "secretary analogy" (notepad vs filing cabinet), and staged implementation plan
