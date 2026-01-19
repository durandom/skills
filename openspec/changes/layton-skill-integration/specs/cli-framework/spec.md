## MODIFIED Requirements

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
