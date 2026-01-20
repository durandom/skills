# Project Instructions Spec

Delta spec for project instructions reference documentation and examples.

## ADDED Requirements

### Requirement: Reference document for best practices

Layton SHALL provide a reference document at `references/project-instructions.md` that documents best practices for CLAUDE.md and AGENTS.md files.

#### Scenario: Reference document exists

- **WHEN** Layton skill is loaded
- **THEN** `references/project-instructions.md` exists
- **AND** document covers separation of concerns between CLAUDE.md and AGENTS.md

#### Scenario: Reference covers CLAUDE.md purpose

- **WHEN** user reads `references/project-instructions.md`
- **THEN** document explains CLAUDE.md is for human-readable project context
- **AND** includes guidance on: repo description, entry points, folder structure, key files

#### Scenario: Reference covers AGENTS.md purpose

- **WHEN** user reads `references/project-instructions.md`
- **THEN** document explains AGENTS.md is for mechanical agent rules
- **AND** includes guidance on: quick references, session protocols, critical rules

#### Scenario: Reference includes anti-patterns

- **WHEN** user reads `references/project-instructions.md`
- **THEN** document lists anti-patterns to avoid
- **AND** includes: excessive verbosity, duplication between files, missing mandatory sections

### Requirement: Example CLAUDE.md file

Layton SHALL provide an example CLAUDE.md at `examples/CLAUDE.md` that demonstrates best practices.

#### Scenario: Example CLAUDE.md exists

- **WHEN** Layton skill is loaded
- **THEN** `examples/CLAUDE.md` exists
- **AND** file is a genericized template (not copy of specific repo)

#### Scenario: Example CLAUDE.md has key sections

- **WHEN** user reads `examples/CLAUDE.md`
- **THEN** file includes: mandatory section at top, repo description, primary entry point, folder structure

### Requirement: Example AGENTS.md file

Layton SHALL provide an example AGENTS.md at `examples/AGENTS.md` that demonstrates best practices.

#### Scenario: Example AGENTS.md exists

- **WHEN** Layton skill is loaded
- **THEN** `examples/AGENTS.md` exists
- **AND** file is concise (under 50 lines)

#### Scenario: Example AGENTS.md has key sections

- **WHEN** user reads `examples/AGENTS.md`
- **THEN** file includes: quick reference commands, session completion protocol, critical rules

## Test Mapping

| Scenario | Test File | Test Function |
|----------|-----------|---------------|
| Reference exists | `tests/layton/unit/test_project_instructions.py` | `test_reference_doc_exists` |
| Reference covers CLAUDE.md | `tests/layton/unit/test_project_instructions.py` | `test_reference_covers_claude_md` |
| Reference covers AGENTS.md | `tests/layton/unit/test_project_instructions.py` | `test_reference_covers_agents_md` |
| Reference anti-patterns | `tests/layton/unit/test_project_instructions.py` | `test_reference_includes_antipatterns` |
| Example CLAUDE.md exists | `tests/layton/unit/test_project_instructions.py` | `test_example_claude_md_exists` |
| Example CLAUDE.md sections | `tests/layton/unit/test_project_instructions.py` | `test_example_claude_md_sections` |
| Example AGENTS.md exists | `tests/layton/unit/test_project_instructions.py` | `test_example_agents_md_exists` |
| Example AGENTS.md sections | `tests/layton/unit/test_project_instructions.py` | `test_example_agents_md_sections` |
