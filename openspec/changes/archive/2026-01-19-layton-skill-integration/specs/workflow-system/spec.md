## ADDED Requirements

### Requirement: Workflow file format

Workflow files SHALL use YAML frontmatter with markdown body, stored in `.layton/workflows/<name>.md`.

#### Scenario: Valid workflow file structure

- **WHEN** a workflow file exists at `.layton/workflows/morning-briefing.md`
- **THEN** it SHALL have YAML frontmatter with `name`, `description`, and `triggers` fields
- **AND** the markdown body SHALL contain AI-readable instructions

#### Scenario: Frontmatter fields

- **WHEN** parsing a workflow file's frontmatter
- **THEN** `name` SHALL be a lowercase identifier matching the filename (without `.md`)
- **AND** `description` SHALL describe what this workflow does
- **AND** `triggers` SHALL be an array of phrases that activate this workflow

---

### Requirement: Workflow file template

The CLI SHALL provide a template for bootstrapping new workflow files.

#### Scenario: Template content

- **WHEN** `layton workflows add <name>` is run
- **THEN** CLI SHALL create `.layton/workflows/<name>.md` with this template:

```markdown
---
name: <name>
description: <what this workflow does>
triggers:
  - <phrase that activates this workflow>
  - <another trigger phrase>
---

## Objective

<!-- What this workflow accomplishes -->

## Steps

<!-- AI-readable instructions for executing this workflow -->

1. Get context:
   ```bash
   layton context
   ```

1. <!-- Next step -->

1. <!-- Next step -->

## Context Adaptation

<!-- How to adapt based on time/context -->

- If morning + work hours: ...
- If evening: ...

## Success Criteria

<!-- How to know the workflow completed successfully -->

- [ ]
- [ ]

```

#### Scenario: Template sections purpose

- **WHEN** AI reads a workflow file
- **THEN** `## Objective` SHALL describe the goal of the workflow
- **AND** `## Steps` SHALL contain numbered AI instructions with commands
- **AND** `## Context Adaptation` SHALL guide behavior based on temporal context
- **AND** `## Success Criteria` SHALL define completion conditions

#### Scenario: Template does not overwrite

- **WHEN** `layton workflows add <name>` is run AND `.layton/workflows/<name>.md` exists
- **THEN** CLI SHALL return error with code `WORKFLOW_EXISTS`
- **AND** error message SHALL suggest reviewing existing file

---

### Requirement: List user workflows

The CLI SHALL list workflows from `.layton/workflows/`.

#### Scenario: List with JSON output

- **WHEN** `layton workflows` is run
- **THEN** output SHALL be JSON with `success` and `workflows` array
- **AND** each workflow SHALL include `name`, `description`, `triggers` from frontmatter

#### Scenario: Empty workflows directory

- **WHEN** `layton workflows` is run AND `.layton/workflows/` is empty or missing
- **THEN** output SHALL have empty `workflows` array
- **AND** `next_steps` SHALL suggest `layton workflows add`

---

### Requirement: Workflows directory creation

The CLI SHALL create `.layton/workflows/` directory when needed.

#### Scenario: Auto-create on add

- **WHEN** `layton workflows add <name>` is run AND `.layton/workflows/` doesn't exist
- **THEN** CLI SHALL create the directory before creating the workflow file

---

### Requirement: Example workflows

Example workflows SHALL exist in `skills/layton/examples/` as reference patterns.

#### Scenario: Examples are reference only

- **WHEN** AI needs to help user create a workflow
- **THEN** AI MAY read examples from `skills/layton/examples/` for inspiration
- **AND** AI SHALL use `layton workflows add` to create user's workflow (not copy examples)
