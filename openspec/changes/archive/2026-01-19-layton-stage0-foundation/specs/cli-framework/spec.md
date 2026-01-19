# CLI Framework Specification

Global behavior for the `layton` CLI. Individual commands have their own specs.

Follows [agentic-cli patterns](../../../../recipes/agentic-cli.md): non-interactive, sensible defaults, next-step hints, hidden destructive flags.

**Agent-first design:** Unlike typical CLIs, Layton defaults to JSON output because its primary consumer is SKILL.md (an AI agent). Humans use `--human` for debugging.

## ADDED Requirements

### Requirement: No-arg invocation

Running `layton` with no arguments SHALL do something useful (not dump help).

#### Scenario: Layton with no args runs doctor

- **WHEN** user runs `layton` with no arguments
- **THEN** CLI SHALL run `layton doctor` (safe, read-only health check)
- **AND** output SHALL include `next_steps` for common actions

#### Scenario: Layton config with no subcommand

- **WHEN** user runs `layton config` with no subcommand
- **THEN** CLI SHALL run `layton config show` (safe, read-only)
- **AND** if config missing, SHALL suggest `layton config init`

---

### Requirement: Global CLI options

The CLI SHALL support global options available on all commands.

#### Scenario: Human output flag

- **WHEN** user runs any command with `--human` flag
- **THEN** output SHALL be formatted for human readability (colors, tables, etc.)
- **AND** output MAY include progress messages

#### Scenario: Verbose flag

- **WHEN** user runs any command with `--verbose` flag
- **THEN** output SHALL include additional debug information in the JSON response

#### Scenario: Help flag

- **WHEN** user runs any command with `--help` flag
- **THEN** CLI SHALL display help text for that command (human-readable)

#### Scenario: Version flag

- **WHEN** user runs `layton --version`
- **THEN** CLI SHALL display the package version

---

### Requirement: Output format consistency

All CLI commands SHALL follow consistent JSON output format.

#### Scenario: Success response structure

- **WHEN** any command succeeds
- **THEN** output SHALL include `"success": true` and `"next_steps": []` array

#### Scenario: Error response structure

- **WHEN** any command fails
- **THEN** output SHALL include `"success": false` and `"error": {"code": "...", "message": "..."}`
- **AND** output SHALL include `"next_steps"` with recovery suggestions

#### Scenario: Exit codes

- **WHEN** command succeeds
- **THEN** exit code SHALL be 0
- **WHEN** command has fixable issues
- **THEN** exit code SHALL be 1
- **WHEN** command has critical issues
- **THEN** exit code SHALL be 2

---

### Requirement: JSON output by default (agent-first)

JSON output SHALL be the default; human output requires explicit flag.

#### Scenario: Default output is JSON

- **WHEN** user runs any command without flags
- **THEN** output SHALL be valid JSON with consistent structure
- **AND** output SHALL be a single JSON object (no progress messages or spinners)

#### Scenario: Human output for debugging

- **WHEN** user runs any command with `--human`
- **THEN** output SHALL be formatted for human readability (colors, tables, etc.)
- **AND** output MAY include progress messages or spinners
