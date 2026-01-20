# Retrospect Workflow Spec

Delta spec for the post-workflow retrospection workflow.

## ADDED Requirements

### Requirement: Retrospect workflow file exists

Layton SHALL provide a retrospect workflow at `workflows/retrospect.md` for post-workflow reflection.

#### Scenario: Workflow file exists

- **WHEN** Layton skill is loaded
- **THEN** `workflows/retrospect.md` exists
- **AND** file has valid YAML frontmatter with name, description, triggers

#### Scenario: Workflow has appropriate triggers

- **WHEN** user reads `workflows/retrospect.md`
- **THEN** triggers include phrases like "retrospect", "reflect on workflow", "workflow feedback"

### Requirement: Retrospect asks structured questions

The retrospect workflow SHALL guide reflection through structured questions about the workflow just completed.

#### Scenario: Identifies the workflow

- **WHEN** retrospect workflow is executed
- **THEN** workflow asks "What workflow did we just complete?"
- **AND** accepts workflow name or description

#### Scenario: Evaluates goal achievement

- **WHEN** retrospect workflow is executed
- **THEN** workflow asks "Did the workflow achieve its goal?"
- **AND** captures yes/no/partial with explanation

#### Scenario: Identifies friction points

- **WHEN** retrospect workflow is executed
- **THEN** workflow asks "What was friction or missing?"
- **AND** captures specific pain points

#### Scenario: Suggests improvements

- **WHEN** retrospect workflow is executed
- **THEN** workflow asks "What adjustments would improve this workflow?"
- **AND** captures concrete suggestions

### Requirement: Retrospect offers to capture changes

The retrospect workflow SHALL offer to propose edits to the workflow file based on feedback.

#### Scenario: Offer to edit workflow

- **WHEN** user provides improvement suggestions
- **THEN** workflow offers to draft edits to the original workflow file
- **AND** user confirms before any edits are proposed

#### Scenario: No edits if declined

- **WHEN** user declines to edit workflow
- **THEN** workflow thanks user for feedback
- **AND** no workflow files are modified

## Test Mapping

| Scenario | Test File | Test Function |
|----------|-----------|---------------|
| Workflow exists | `tests/layton/unit/test_workflows.py` | `test_retrospect_workflow_exists` |
| Workflow triggers | `tests/layton/unit/test_workflows.py` | `test_retrospect_workflow_triggers` |
| Structured questions | (manual/integration) | N/A - workflow execution |
