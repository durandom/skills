# cli-doctor Specification

## Purpose

TBD - created by archiving change layton-stage0-foundation. Update Purpose after archive.

## Requirements

### Requirement: Health check categories

Doctor SHALL check multiple categories with clear pass/fail status.

#### Scenario: All checks pass

- **WHEN** `bd` CLI is available AND config is valid
- **THEN** command SHALL return exit code 0
- **AND** output SHALL include `"success": true`

#### Scenario: Check result structure

- **WHEN** user runs `layton doctor`
- **THEN** output SHALL be JSON and include `"checks"` array with objects containing:
  - `"name"`: Check identifier (e.g., `"beads_available"`)
  - `"status"`: One of `"pass"`, `"warn"`, `"fail"`
  - `"message"`: Human-readable explanation

---

### Requirement: Beads availability check

Doctor SHALL verify the `bd` CLI is installed and accessible.

#### Scenario: Beads CLI available

- **WHEN** `bd` command is found in PATH AND `bd info --json` succeeds
- **THEN** `beads_available` check SHALL have `"status": "pass"`

#### Scenario: Beads CLI missing

- **WHEN** `bd` CLI is not found in PATH
- **THEN** command SHALL return exit code 2 (critical)
- **AND** output SHALL include check with `"status": "fail"` and `"name": "beads_available"`
- **AND** `next_steps` SHALL suggest installing Beads

#### Scenario: Beads not initialized

- **WHEN** `bd` is available but `.beads/` directory does not exist
- **THEN** `beads_initialized` check SHALL have `"status": "warn"` (not fail)
- **AND** `next_steps` SHALL suggest `bd init`

---

### Requirement: Config check

Doctor SHALL verify Layton configuration exists.

#### Scenario: Config exists

- **WHEN** `.layton/config.json` exists and is valid JSON
- **THEN** `config_exists` check SHALL have `"status": "pass"`

#### Scenario: Config missing but fixable

- **WHEN** `.layton/config.json` does not exist
- **THEN** command SHALL return exit code 1 (fixable)
- **AND** `config_exists` check SHALL have `"status": "fail"`
- **AND** `next_steps` SHALL include `layton doctor --fix`

#### Scenario: Config invalid JSON

- **WHEN** `.layton/config.json` exists but is not valid JSON
- **THEN** `config_valid` check SHALL have `"status": "fail"`
- **AND** message SHALL explain the JSON parse error

---

### Requirement: Fix flag

Doctor SHALL support a hidden `--fix` flag to auto-repair fixable issues.

#### Scenario: Fix flag creates config

- **WHEN** user runs `layton doctor --fix` AND config is missing
- **THEN** command SHALL create `.layton/config.json` with defaults
- **AND** command SHALL return exit code 0

#### Scenario: Fix flag is hidden

- **WHEN** user runs `layton doctor --help`
- **THEN** `--fix` flag SHALL NOT appear in help text
- **AND** `--fix` SHALL appear in `next_steps` when issues are fixable

#### Scenario: Fix cannot resolve critical issues

- **WHEN** user runs `layton doctor --fix` AND `bd` CLI is missing
- **THEN** command SHALL still return exit code 2
- **AND** message SHALL explain that Beads must be installed manually

---

### Requirement: Summary output

Doctor SHALL provide a clear summary for humans when requested.

#### Scenario: Human output summary

- **WHEN** user runs `layton doctor --human`
- **THEN** output SHALL show each check with pass/warn/fail indicator
- **AND** output SHALL end with overall status and next steps

#### Scenario: All pass message

- **WHEN** all checks pass AND `--human` flag is used
- **THEN** output SHALL include encouraging message (e.g., "All systems go!")
