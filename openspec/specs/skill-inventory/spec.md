## ADDED Requirements

### Requirement: Skill file format

Skill files SHALL use YAML frontmatter with markdown body, stored in `.layton/skills/<name>.md`.

#### Scenario: Valid skill file structure

- **WHEN** a skill file exists at `.layton/skills/gtd.md`
- **THEN** it SHALL have YAML frontmatter with `name`, `description`, and `source` fields
- **AND** the markdown body SHALL contain instructions for querying the skill

#### Scenario: Frontmatter fields

- **WHEN** parsing a skill file's frontmatter
- **THEN** `name` SHALL be a lowercase identifier matching the filename (without `.md`)
- **AND** `description` SHALL describe when/why to query this skill
- **AND** `source` SHALL be the path to the source SKILL.md (e.g., `skills/gtd/SKILL.md`)

---

### Requirement: Skill file template

The CLI SHALL provide a template for bootstrapping new skill files.

#### Scenario: Template content

- **WHEN** `layton skills add <name>` is run
- **THEN** CLI SHALL create `.layton/skills/<name>.md` with this template:

```markdown
---
name: <name>
description: <when/why to query this skill>
source: skills/<name>/SKILL.md
---

## Commands

<!-- Commands to run when gathering data from this skill -->
<!-- Run from repo root -->

```bash
# Example:
# SKILL="./.claude/skills/<name>/scripts/<name>"
# $SKILL <command>
```

## What to Extract

<!-- Key information to look for in the output -->

-
-

## Key Metrics

<!-- Important numbers or states to surface in briefings -->

| Metric | Meaning |
|--------|---------|
|        |         |

```

#### Scenario: Template sections purpose

- **WHEN** AI reads a skill file
- **THEN** `## Commands` SHALL contain bash commands to execute for data gathering
- **AND** `## What to Extract` SHALL guide what information matters from the output
- **AND** `## Key Metrics` SHALL define important indicators for briefings

#### Scenario: Template does not overwrite

- **WHEN** `layton skills add <name>` is run AND `.layton/skills/<name>.md` exists
- **THEN** CLI SHALL return error with code `SKILL_EXISTS`
- **AND** error message SHALL suggest reviewing existing file

---

### Requirement: Skill discovery

The CLI SHALL discover external skills by scanning the `skills/` directory.

#### Scenario: Discover available skills

- **WHEN** `layton skills --discover` is run
- **THEN** CLI SHALL scan `skills/*/SKILL.md` for available skills
- **AND** output SHALL include `known` array (skills with files in `.layton/skills/`)
- **AND** output SHALL include `unknown` array (skills without files)

#### Scenario: Discovery extracts metadata

- **WHEN** scanning a SKILL.md file
- **THEN** CLI SHALL extract `name` and `description` from YAML frontmatter
- **AND** unknown skills output SHALL include this metadata

#### Scenario: Self-exclusion

- **WHEN** discovering skills
- **THEN** CLI SHALL exclude `skills/layton/SKILL.md` from results (Layton doesn't query itself)

---

### Requirement: List known skills

The CLI SHALL list skills from `.layton/skills/`.

#### Scenario: List with JSON output

- **WHEN** `layton skills` is run
- **THEN** output SHALL be JSON with `success` and `skills` array
- **AND** each skill SHALL include `name`, `description`, `source` from frontmatter

#### Scenario: Empty skills directory

- **WHEN** `layton skills` is run AND `.layton/skills/` is empty or missing
- **THEN** output SHALL have empty `skills` array
- **AND** `next_steps` SHALL suggest `layton skills --discover` and `layton skills add`

---

### Requirement: Skills directory creation

The CLI SHALL create `.layton/skills/` directory when needed.

#### Scenario: Auto-create on add

- **WHEN** `layton skills add <name>` is run AND `.layton/skills/` doesn't exist
- **THEN** CLI SHALL create the directory before creating the skill file
