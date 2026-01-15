## Why

The original Layton planning (`001-pai-orchestrator/`) was too ambitious - spanning 27 functional requirements across GTD, Calendar, Jira, Email, and Slack integration. This stage establishes the foundation: a minimal CLI that verifies Beads integration and provides temporal context, before adding skill aggregation or AI synthesis.

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

- `layton-cli`: The deterministic CLI providing doctor, context, and config commands
- `layton-config`: Personal configuration schema and loading (work schedule, timezone, personality, interaction preferences)
- `beads-conventions`: How Layton uses Beads for state management (tags, bead types, conventions)

### Modified Capabilities

(None - this is greenfield)

## Impact

- **New files**: `skills/layton/` directory structure with CLI and SKILL.md
- **Dependencies**: Requires `bd` CLI (Beads) to be installed
- **Config files**: Creates `.layton/config.json` per-repo (gitignore-able)
- **No breaking changes**: This is additive

## References

- **[.planning/layton.md](../../../.planning/layton.md)** - Exploration session summary with architecture decisions, the "secretary analogy" (notepad vs filing cabinet), and staged implementation plan
- **[001-pai-orchestrator/](../../../001-pai-orchestrator/)** - Original planning documents (spec, user stories, data model, CLI contract)
