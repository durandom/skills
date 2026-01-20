# cli-framework Specification

## Purpose

TBD - created by archiving change layton-stage0-foundation. Update Purpose after archive.

## Requirements

### Requirement: No-arg invocation

Running `layton` with no arguments SHALL return full AI orientation (doctor + skills + workflows).

#### Scenario: Layton with no args returns orientation

- **WHEN** user runs `layton` with no arguments
- **THEN** CLI SHALL return JSON with `checks` (doctor output), `skills` (from `.layton/skills/`), and `workflows` (from `.layton/workflows/`)
- **AND** output SHALL include `next_steps` for common actions

#### Scenario: Orientation includes doctor checks

- **WHEN** user runs `layton` with no arguments
- **THEN** `checks` field SHALL contain all doctor check results (beads, config validity)

#### Scenario: Orientation includes skills inventory

- **WHEN** user runs `layton` with no arguments
- **THEN** `skills` field SHALL be an array of known skills
- **AND** each skill SHALL include `name` and `description` from frontmatter

#### Scenario: Orientation includes workflows inventory

- **WHEN** user runs `layton` with no arguments
- **THEN** `workflows` field SHALL be an array of user workflows
- **AND** each workflow SHALL include `name`, `description`, and `triggers` from frontmatter

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
