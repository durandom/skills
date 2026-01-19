# cli-config Specification

## Purpose

TBD - created by archiving change layton-stage0-foundation. Update Purpose after archive.

## Requirements

### Requirement: Config file location

The config file SHALL be stored at `.layton/config.json` relative to the git root.

#### Scenario: Config in git root

- **WHEN** CLI runs in a git repository
- **THEN** config path SHALL be `<git-root>/.layton/config.json`

#### Scenario: Config outside git

- **WHEN** CLI runs outside a git repository
- **THEN** config path SHALL be `./.layton/config.json` (current directory)

---

### Requirement: Config as key-value store

The config SHALL behave as a simple key-value store with dot-notation access.

#### Scenario: Flat keys

- **WHEN** user runs `layton config get timezone`
- **THEN** CLI SHALL return the value of the `timezone` key

#### Scenario: Nested keys with dot notation

- **WHEN** user runs `layton config get work.schedule.start`
- **THEN** CLI SHALL traverse `work` → `schedule` → `start` and return the value

#### Scenario: Missing key returns error

- **WHEN** user runs `layton config get nonexistent.key`
- **THEN** CLI SHALL return error with code `KEY_NOT_FOUND`

---

### Requirement: Config init command

The `layton config init` command SHALL create a config file with sensible defaults.

#### Scenario: Init creates config

- **WHEN** user runs `layton config init` AND no config exists
- **THEN** CLI SHALL create `.layton/config.json` with sensible defaults

#### Scenario: Init sensible defaults

- **WHEN** config is created via init
- **THEN** it SHALL include at minimum: `work.schedule.start`, `work.schedule.end`, `timezone`

#### Scenario: Init does not overwrite

- **WHEN** user runs `layton config init` AND config already exists
- **THEN** CLI SHALL return error and NOT overwrite
- **AND** error message SHALL suggest `--force` if intentional

#### Scenario: Init with force overwrites

- **WHEN** user runs `layton config init --force`
- **THEN** CLI SHALL overwrite existing config with defaults

---

### Requirement: Config show command

The `layton config show` command SHALL display the entire config file.

#### Scenario: Show dumps config (default JSON)

- **WHEN** user runs `layton config show`
- **THEN** output SHALL be wrapped in standard response format with `success` and `config` fields

#### Scenario: Show human-readable

- **WHEN** user runs `layton config show --human`
- **THEN** CLI SHALL output the config as formatted, syntax-highlighted JSON

#### Scenario: Show when missing

- **WHEN** user runs `layton config show` AND no config exists
- **THEN** CLI SHALL return error with code `CONFIG_MISSING`
- **AND** `next_steps` SHALL suggest `layton config init`

---

### Requirement: Config keys command

The `layton config keys` command SHALL list all keys for discovery.

#### Scenario: Keys lists all paths (default JSON)

- **WHEN** user runs `layton config keys`
- **THEN** output SHALL be a JSON object with `success` and `keys` array

#### Scenario: Keys example output

- **WHEN** config contains `{"work": {"schedule": {"start": "09:00"}}}`
- **THEN** `layton config keys` SHALL include `"work.schedule.start"` in the `keys` array

#### Scenario: Keys human-readable

- **WHEN** user runs `layton config keys --human`
- **THEN** CLI SHALL output all key paths (dot notation) one per line

---

### Requirement: Config get command

The `layton config get` command SHALL retrieve a single value.

#### Scenario: Get returns raw value

- **WHEN** user runs `layton config get timezone`
- **THEN** CLI SHALL output just the value (e.g., `America/Los_Angeles`)

#### Scenario: Get nested value

- **WHEN** user runs `layton config get work.schedule.start`
- **THEN** CLI SHALL output just the value (e.g., `09:00`)

#### Scenario: Get object returns JSON

- **WHEN** user runs `layton config get work.schedule`
- **THEN** CLI SHALL output the object as JSON (e.g., `{"start": "09:00", "end": "17:00"}`)

---

### Requirement: Config set command

The `layton config set` command SHALL update a single value.

#### Scenario: Set updates value

- **WHEN** user runs `layton config set timezone "Europe/London"`
- **THEN** CLI SHALL update the `timezone` key in config file

#### Scenario: Set creates nested path

- **WHEN** user runs `layton config set my.custom.field "value"` AND path doesn't exist
- **THEN** CLI SHALL create the nested structure

#### Scenario: Set with JSON value

- **WHEN** user runs `layton config set work.schedule '{"start": "08:00", "end": "16:00"}'`
- **THEN** CLI SHALL parse and store as object, not string

---

### Requirement: No runtime default merging

The CLI SHALL NOT merge defaults at runtime.

#### Scenario: Missing keys stay missing

- **WHEN** config exists but lacks a key the CLI needs
- **THEN** CLI SHALL fail with clear error, NOT silently use defaults

#### Scenario: Init is the only default source

- **WHEN** user wants default values
- **THEN** they SHALL run `layton config init` to get them
- **AND** CLI SHALL NOT inject defaults during normal operation
