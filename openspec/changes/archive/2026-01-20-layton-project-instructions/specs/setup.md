# Setup Workflow Spec

Delta spec for modifications to the existing setup workflow.

## MODIFIED Requirements

### Requirement: Setup mentions audit workflow

The setup workflow SHALL mention the audit-project-instructions workflow as an optional step for users who want to review their project instruction files.

#### Scenario: Setup offers audit during onboarding

- **WHEN** setup workflow reaches the "Suggest Workflows" step
- **THEN** workflow mentions the audit-project-instructions workflow
- **AND** explains it can help organize CLAUDE.md and AGENTS.md

#### Scenario: User can skip audit mention

- **WHEN** setup workflow mentions audit workflow
- **THEN** it is presented as optional ("Would you like to...")
- **AND** setup continues regardless of user response

#### Scenario: User interested in audit

- **WHEN** user expresses interest in auditing project instructions
- **THEN** setup suggests running the audit workflow after setup completes
- **AND** does NOT invoke audit workflow inline (keeps setup focused)

## Test Mapping

| Scenario | Test File | Test Function |
|----------|-----------|---------------|
| Setup mentions audit | `tests/layton/unit/test_workflows.py` | `test_setup_mentions_audit_workflow` |
| Audit mention is optional | (manual/integration) | N/A - workflow execution |
