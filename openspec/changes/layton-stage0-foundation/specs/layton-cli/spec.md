# Layton CLI Specification

The `layton` CLI provides deterministic operations for Stage 0. All probabilistic work (AI judgment, synthesis) lives in SKILL.md workflows.

Follows [agentic-cli patterns](../../../../recipes/agentic-cli.md): non-interactive, sensible defaults, next-step hints, hidden destructive flags.

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

#### Scenario: JSON output flag

- **WHEN** user runs any command with `--json` flag
- **THEN** output SHALL be valid JSON with consistent structure

#### Scenario: Verbose flag

- **WHEN** user runs any command with `--verbose` flag
- **THEN** output SHALL include additional debug information

#### Scenario: Help flag

- **WHEN** user runs any command with `--help` flag
- **THEN** CLI SHALL display help text for that command

---

### Requirement: layton doctor command

The `layton doctor` command SHALL validate system setup and dependencies.

#### Scenario: All checks pass

- **WHEN** `bd` CLI is available AND config is valid
- **THEN** command SHALL return exit code 0
- **AND** output SHALL include `"success": true`

#### Scenario: Beads CLI missing

- **WHEN** `bd` CLI is not found in PATH
- **THEN** command SHALL return exit code 2 (critical)
- **AND** output SHALL include check with `"status": "fail"` and `"name": "beads_available"`

#### Scenario: Config missing but fixable

- **WHEN** `.layton/config.json` does not exist
- **THEN** command SHALL return exit code 1 (fixable)
- **AND** `next_steps` SHALL include `layton doctor --fix`

#### Scenario: Fix flag creates config

- **WHEN** user runs `layton doctor --fix` AND config is missing
- **THEN** command SHALL create `.layton/config.json` with defaults
- **AND** command SHALL return exit code 0

#### Scenario: Fix flag is hidden

- **WHEN** user runs `layton doctor --help`
- **THEN** `--fix` flag SHALL NOT appear in help text
- **AND** `--fix` SHALL appear in `next_steps` when issues are fixable

---

### Requirement: layton context command

The `layton context` command SHALL return temporal context for SKILL.md workflows.

#### Scenario: Basic context output

- **WHEN** user runs `layton context --json`
- **THEN** output SHALL include `timestamp`, `time_of_day`, `day_of_week`, `work_hours`, `timezone`

#### Scenario: Time of day classification - morning

- **WHEN** current time is between 05:00 and 11:59
- **THEN** `time_of_day` SHALL be `"morning"`

#### Scenario: Time of day classification - midday

- **WHEN** current time is between 12:00 and 13:59
- **THEN** `time_of_day` SHALL be `"midday"`

#### Scenario: Time of day classification - afternoon

- **WHEN** current time is between 14:00 and 17:59
- **THEN** `time_of_day` SHALL be `"afternoon"`

#### Scenario: Time of day classification - evening

- **WHEN** current time is between 18:00 and 21:59
- **THEN** `time_of_day` SHALL be `"evening"`

#### Scenario: Time of day classification - night

- **WHEN** current time is between 22:00 and 04:59
- **THEN** `time_of_day` SHALL be `"night"`

#### Scenario: Work hours from config

- **WHEN** config specifies `work.schedule.start` and `work.schedule.end`
- **THEN** `work_hours` SHALL be `true` if current time is within that range

#### Scenario: Work hours config missing

- **WHEN** config does not exist OR lacks `work.schedule`
- **THEN** command SHALL return error with code `CONFIG_MISSING`
- **AND** `next_steps` SHALL suggest `layton config init`

---

### Requirement: layton config command

The `layton config` command SHALL manage personal configuration as a key-value store.

#### Scenario: Config subcommands

- **WHEN** user runs `layton config --help`
- **THEN** CLI SHALL show subcommands: `init`, `show`, `keys`, `get`, `set`

#### Scenario: Config init

- **WHEN** user runs `layton config init`
- **THEN** CLI SHALL create `.layton/config.json` with sensible defaults
- **AND** SHALL NOT overwrite if file exists (use `--force` to overwrite)

#### Scenario: Config show

- **WHEN** user runs `layton config show`
- **THEN** CLI SHALL output the entire config file as formatted JSON

#### Scenario: Config keys for discovery

- **WHEN** user runs `layton config keys`
- **THEN** CLI SHALL list all key paths (dot notation) for discovery

#### Scenario: Config get single value

- **WHEN** user runs `layton config get work.schedule.start`
- **THEN** CLI SHALL output just the value (e.g., `09:00`)

#### Scenario: Config set single value

- **WHEN** user runs `layton config set timezone "Europe/London"`
- **THEN** CLI SHALL update the key in config file
- **AND** SHALL create nested path if it doesn't exist

---

### Requirement: Output format consistency

All CLI commands SHALL follow consistent output format.

#### Scenario: Success response structure

- **WHEN** any command succeeds with `--json`
- **THEN** output SHALL include `"success": true` and `"next_steps": []` array

#### Scenario: Error response structure

- **WHEN** any command fails with `--json`
- **THEN** output SHALL include `"success": false` and `"error": {"code": "...", "message": "..."}`
- **AND** output SHALL include `"next_steps"` with recovery suggestions

#### Scenario: Exit codes

- **WHEN** command succeeds
- **THEN** exit code SHALL be 0
- **WHEN** command has fixable issues
- **THEN** exit code SHALL be 1
- **WHEN** command has critical issues
- **THEN** exit code SHALL be 2
