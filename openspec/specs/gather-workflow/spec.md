## ADDED Requirements

### Requirement: Gather workflow is an example

The gather workflow SHALL be an example workflow at `skills/layton/examples/gather.md`.

#### Scenario: Example location

- **WHEN** user wants to gather data from skills
- **THEN** they SHALL first create a workflow using `layton workflows add gather`
- **AND** they MAY reference `skills/layton/examples/gather.md` for guidance

---

### Requirement: Gather reads skill files

The gather workflow SHALL read skill files from `.layton/skills/`.

#### Scenario: Skill file iteration

- **WHEN** AI follows a gather workflow
- **THEN** it SHALL read each file in `.layton/skills/`
- **AND** for each skill, it SHALL follow the documented commands

---

### Requirement: Gather executes skill commands

The gather workflow SHALL execute commands documented in skill files.

#### Scenario: Command execution

- **WHEN** AI reads a skill file's `## Commands` section
- **THEN** it SHALL execute those commands
- **AND** it SHALL capture the output for aggregation

#### Scenario: Command failure handling

- **WHEN** a skill command fails (non-zero exit or error)
- **THEN** AI SHALL note the failure in aggregated results
- **AND** AI SHALL continue with remaining skills

---

### Requirement: Gather extracts key information

The gather workflow SHALL extract information per skill file guidance.

#### Scenario: Extraction guidance

- **WHEN** a skill file has a `## What to Extract` section
- **THEN** AI SHALL use that guidance to identify key information from output
- **AND** AI SHALL aggregate extracted information for other workflows

---

### Requirement: Gather aggregates results

The gather workflow SHALL produce aggregated results for consumption.

#### Scenario: Aggregation structure

- **WHEN** AI completes gathering from all skills
- **THEN** results SHALL be organized by skill name
- **AND** results SHALL include extracted key information per skill
