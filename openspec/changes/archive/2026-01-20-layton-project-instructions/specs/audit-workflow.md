# Audit Workflow Spec

Delta spec for the project instructions audit workflow.

## ADDED Requirements

### Requirement: Audit workflow file exists

Layton SHALL provide an audit workflow at `workflows/audit-project-instructions.md` that analyzes target repo instruction files.

#### Scenario: Workflow file exists

- **WHEN** Layton skill is loaded
- **THEN** `workflows/audit-project-instructions.md` exists
- **AND** file has valid YAML frontmatter with name, description, triggers

#### Scenario: Workflow has appropriate triggers

- **WHEN** user reads `workflows/audit-project-instructions.md`
- **THEN** triggers include phrases like "audit project instructions", "review claude md", "check agents md"

### Requirement: Audit reads target files

The audit workflow SHALL read the target repository's CLAUDE.md and AGENTS.md files (if they exist) before analysis.

#### Scenario: Both files exist

- **WHEN** audit workflow is executed AND target repo has CLAUDE.md and AGENTS.md
- **THEN** workflow reads both files
- **AND** proceeds to analysis step

#### Scenario: CLAUDE.md missing

- **WHEN** audit workflow is executed AND target repo has no CLAUDE.md
- **THEN** workflow notes the missing file
- **AND** suggests creating one based on examples

#### Scenario: AGENTS.md missing

- **WHEN** audit workflow is executed AND target repo has no AGENTS.md
- **THEN** workflow notes the missing file
- **AND** suggests creating one based on examples

### Requirement: Audit compares against best practices

The audit workflow SHALL compare target files against the reference document and identify issues.

#### Scenario: Verbosity check

- **WHEN** audit analyzes CLAUDE.md
- **THEN** workflow checks for excessive length or verbosity
- **AND** reports if file exceeds recommended size

#### Scenario: Duplication check

- **WHEN** audit analyzes both files
- **THEN** workflow identifies content duplicated between CLAUDE.md and AGENTS.md
- **AND** suggests which file should own each duplicated section

#### Scenario: Missing sections check

- **WHEN** audit analyzes files
- **THEN** workflow identifies missing recommended sections
- **AND** references the corresponding section in examples

### Requirement: Audit suggests but does not modify

The audit workflow SHALL present findings as suggestions only. It SHALL NOT automatically modify files.

#### Scenario: Findings presented as suggestions

- **WHEN** audit completes analysis
- **THEN** output presents findings with "Consider:" or "Suggestion:" prefix
- **AND** includes rationale for each suggestion

#### Scenario: No auto-apply

- **WHEN** audit completes
- **THEN** no files are modified
- **AND** user is prompted to decide which suggestions to apply

## Test Mapping

| Scenario | Test File | Test Function |
|----------|-----------|---------------|
| Workflow exists | `tests/layton/unit/test_workflows.py` | `test_audit_workflow_exists` |
| Workflow triggers | `tests/layton/unit/test_workflows.py` | `test_audit_workflow_triggers` |
| Both files exist | (manual/integration) | N/A - workflow execution |
| Missing CLAUDE.md | (manual/integration) | N/A - workflow execution |
| Missing AGENTS.md | (manual/integration) | N/A - workflow execution |
