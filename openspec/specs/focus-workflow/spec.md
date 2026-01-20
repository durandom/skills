## ADDED Requirements

### Requirement: Focus workflow is an example

The focus workflow SHALL be an example workflow at `skills/layton/examples/focus-suggestion.md`.

#### Scenario: Example location

- **WHEN** user wants focus suggestions
- **THEN** they SHALL first create a workflow using `layton workflows add focus-suggestion`
- **AND** they MAY reference `skills/layton/examples/focus-suggestion.md` for guidance

---

### Requirement: Focus workflow considers context

The focus workflow SHALL consider temporal and energy context.

#### Scenario: Temporal context

- **WHEN** AI follows a focus workflow
- **THEN** it SHALL run `layton context` to understand time of day and work hours

#### Scenario: Energy matching

- **WHEN** suggesting focus during morning work hours
- **THEN** AI SHALL prefer high-energy tasks
- **WHEN** suggesting focus during evening or low-energy periods
- **THEN** AI SHALL prefer low-energy tasks

---

### Requirement: Focus workflow queries available work

The focus workflow SHALL query available tasks from skills.

#### Scenario: GTD integration

- **WHEN** user has `.layton/skills/gtd.md`
- **THEN** focus workflow SHALL query GTD for active tasks
- **AND** it SHALL consider task context labels (focus, async, meetings)

#### Scenario: Beads integration

- **WHEN** AI follows a focus workflow
- **THEN** it SHALL check `bd list --label watching --json` for tracked items

---

### Requirement: Focus workflow presents options

The focus workflow SHALL present focus options to user.

#### Scenario: Option presentation

- **WHEN** AI has gathered available work
- **THEN** it SHALL present 2-3 recommended options
- **AND** each option SHALL include rationale (why this task, why now)

#### Scenario: User selection

- **WHEN** user selects a focus option
- **THEN** AI SHALL use the set-focus workflow to set it
