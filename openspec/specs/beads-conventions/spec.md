# beads-conventions Specification

## Purpose

TBD - created by archiving change layton-stage0-foundation. Update Purpose after archive.

## Requirements

### Requirement: Beads as primary state store

Layton SHALL use Beads for all mutable state management.

#### Scenario: No custom state files

- **WHEN** Layton needs to track state
- **THEN** it SHALL use Beads (`.beads/`) NOT custom files like `.layton/state.json`

#### Scenario: Config is not state

- **WHEN** Layton stores personal configuration
- **THEN** it SHALL use `.layton/config.json` (stable settings, not mutable state)

---

### Requirement: Tag conventions for Layton beads

Layton SHALL use simple labels (not `bd state`) for Stage 0. State machine pattern MAY be adopted in future stages.

#### Scenario: Watching label for attention items

- **WHEN** user asks Layton to track an item
- **THEN** SKILL.md SHALL create bead with label `watching`
- **AND** example: `bd create "JIRA-1234: blocking release" -t task -p 2 -l watching,layton --json`

#### Scenario: Focus label for current work

- **WHEN** user sets current focus
- **THEN** SKILL.md SHALL create/update bead with label `focus`
- **AND** only ONE bead SHOULD have `focus` label at a time
- **AND** previous focus bead SHOULD have `focus` label removed

#### Scenario: Layton namespace label

- **WHEN** Layton creates any bead
- **THEN** bead SHALL include label `layton` for filtering
- **AND** example: `bd list --label layton --json`

#### Scenario: Source system labels

- **WHEN** tracking an item from an external system (Jira, GitHub, etc.)
- **THEN** bead SHOULD include system-specific label
- **AND** example: `bd create "..." -t task -p 2 -l watching,jira,layton --json`

---

### Requirement: Bead description conventions

Bead descriptions SHALL follow a consistent format for AI parsing.

#### Scenario: External reference format

- **WHEN** tracking an external item
- **THEN** description SHALL start with system ID
- **AND** example: `"JIRA-1234: blocking release - promised Kim to check Monday"`

#### Scenario: Context after colon

- **WHEN** bead has user context
- **THEN** context SHALL follow the ID after a colon separator
- **AND** this allows splitting ID from annotation

---

### Requirement: Querying Layton beads

SKILL.md workflows SHALL query beads using standard `bd` commands with `--json` flag.

#### Scenario: List watched items

- **WHEN** SKILL.md needs attention items
- **THEN** it SHALL run `bd list --label watching --json`

#### Scenario: List current focus

- **WHEN** SKILL.md needs current focus
- **THEN** it SHALL run `bd list --label focus --json`

#### Scenario: List all Layton beads

- **WHEN** SKILL.md needs all Layton-managed beads
- **THEN** it SHALL run `bd list --label layton --json`

#### Scenario: Check ready work

- **WHEN** SKILL.md needs unblocked tasks
- **THEN** it SHALL run `bd ready --json`

---

### Requirement: Beads availability check

`layton doctor` SHALL verify Beads is available.

#### Scenario: bd CLI in PATH

- **WHEN** `bd info --json` succeeds
- **THEN** `beads_available` check SHALL pass

#### Scenario: bd CLI missing

- **WHEN** `bd` command is not found
- **THEN** `beads_available` check SHALL fail
- **AND** status SHALL be `"fail"` (critical, not fixable by Layton)

#### Scenario: beads not initialized

- **WHEN** `bd` is available but `.beads/` directory does not exist
- **THEN** doctor SHALL warn but not fail
- **AND** `next_steps` SHALL suggest `bd init`

---

### Requirement: SKILL.md direct Beads usage

SKILL.md workflows SHALL invoke `bd` directly, not via Layton CLI.

#### Scenario: No layton track command

- **WHEN** user asks to track something
- **THEN** SKILL.md SHALL call `bd create ... -l watching,layton --json` directly
- **AND** Layton CLI SHALL NOT have `track`, `untrack`, or `watched` commands

#### Scenario: SKILL.md reads beads for synthesis

- **WHEN** generating morning briefing
- **THEN** SKILL.md SHALL combine:
  - `bd list --label watching --json` (attention items)
  - `bd list --label focus --json` (current focus)
  - `layton context` (temporal context — JSON by default)

#### Scenario: Closing tracked items

- **WHEN** user says "stop tracking X" or "that's done"
- **THEN** SKILL.md SHALL call `bd close <id> --reason "..." --json`

---
