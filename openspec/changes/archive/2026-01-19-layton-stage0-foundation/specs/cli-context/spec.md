# Context Command Specification

The `layton context` command returns temporal context for SKILL.md workflows. This is pure, deterministic output — no AI judgment, just facts about the current time.

## ADDED Requirements

### Requirement: Temporal context output

Context SHALL return structured temporal information.

#### Scenario: Basic context output

- **WHEN** user runs `layton context`
- **THEN** output SHALL be JSON and include:
  - `timestamp`: ISO 8601 datetime
  - `time_of_day`: Classification string
  - `day_of_week`: Day name (e.g., "Monday")
  - `work_hours`: Boolean indicating if within work schedule
  - `timezone`: Timezone from config

---

### Requirement: Time of day classification

Context SHALL classify the current hour into named periods.

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

---

### Requirement: Work hours calculation

Context SHALL determine if current time is within configured work hours.

#### Scenario: Work hours from config

- **WHEN** config specifies `work.schedule.start` and `work.schedule.end`
- **THEN** `work_hours` SHALL be `true` if current time is within that range (inclusive)

#### Scenario: Work hours boundary - start

- **WHEN** current time equals `work.schedule.start`
- **THEN** `work_hours` SHALL be `true`

#### Scenario: Work hours boundary - end

- **WHEN** current time equals `work.schedule.end`
- **THEN** `work_hours` SHALL be `true`

#### Scenario: Outside work hours

- **WHEN** current time is before `work.schedule.start` OR after `work.schedule.end`
- **THEN** `work_hours` SHALL be `false`

---

### Requirement: Config dependency

Context SHALL require valid configuration.

#### Scenario: Work hours config missing

- **WHEN** config does not exist OR lacks `work.schedule`
- **THEN** command SHALL return error with code `CONFIG_MISSING`
- **AND** `next_steps` SHALL suggest `layton config init`

#### Scenario: Timezone from config

- **WHEN** config specifies `timezone`
- **THEN** context SHALL use that timezone for all calculations
- **AND** `timezone` field in output SHALL reflect the configured value

#### Scenario: Timezone config missing

- **WHEN** config lacks `timezone`
- **THEN** command SHALL return error with code `CONFIG_MISSING`
- **AND** message SHALL specify which key is missing

---

### Requirement: Human-readable output

Context SHALL provide friendly output for humans when requested.

#### Scenario: Human output format

- **WHEN** user runs `layton context --human`
- **THEN** output SHALL be formatted for readability
- **AND** output SHALL include natural language summary (e.g., "It's Monday morning, within work hours")
