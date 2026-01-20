## ADDED Requirements

### Requirement: Briefing workflow is an example

The briefing workflow SHALL be an example workflow at `skills/layton/examples/morning-briefing.md`.

#### Scenario: Example location

- **WHEN** user wants morning briefings
- **THEN** they SHALL first create a workflow using `layton workflows add morning-briefing`
- **AND** they MAY reference `skills/layton/examples/morning-briefing.md` for guidance

---

### Requirement: Briefing combines multiple data sources

The briefing workflow SHALL combine temporal context, beads state, and skill data.

#### Scenario: Temporal context

- **WHEN** AI follows a briefing workflow
- **THEN** it SHALL run `layton context` to get time of day, work hours, timezone

#### Scenario: Beads state

- **WHEN** AI follows a briefing workflow
- **THEN** it SHALL run `bd list --label watching --json` to get attention items
- **AND** it SHALL run `bd list --label focus --json` to get current focus

#### Scenario: Skill data

- **WHEN** AI follows a briefing workflow AND user has a gather workflow
- **THEN** it SHALL follow the gather workflow to collect skill data

---

### Requirement: Briefing adapts to context

The briefing workflow SHALL adapt output based on temporal context.

#### Scenario: Morning work hours

- **WHEN** `time_of_day` is `morning` AND `work_hours` is `true`
- **THEN** briefing SHALL be comprehensive with focus suggestions

#### Scenario: Evening outside work hours

- **WHEN** `time_of_day` is `evening` AND `work_hours` is `false`
- **THEN** briefing SHALL be brief summary only

---

### Requirement: Briefing uses persona

The briefing workflow SHALL use the Elizabeth Layton persona.

#### Scenario: Persona voice

- **WHEN** AI delivers a briefing
- **THEN** it SHALL use tone and style from `references/persona.md`

---

### Requirement: Briefing prioritizes information

The briefing workflow SHALL prioritize information appropriately.

#### Scenario: Priority order

- **WHEN** AI synthesizes a briefing
- **THEN** it SHALL present: current focus first, then attention items, then suggestions
