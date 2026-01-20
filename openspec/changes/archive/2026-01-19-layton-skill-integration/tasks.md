## 1. File Structure & Migration

- [x] 1.1 Create `skills/layton/examples/` directory
- [x] 1.2 Move `skills/layton/workflows/morning-briefing.md` → `skills/layton/examples/morning-briefing.md`
- [x] 1.3 Create placeholder `.layton/skills/.gitkeep` for tracking empty directory
- [x] 1.4 Create placeholder `.layton/workflows/.gitkeep` for tracking empty directory

## 2. Skill Inventory CLI (`laytonlib/skills.py`)

- [x] 2.1 Create `skills.py` module with skill file parsing (YAML frontmatter extraction)
- [x] 2.2 Implement `list_skills()` function to scan `.layton/skills/` directory
- [x] 2.3 Implement `discover_skills()` function to scan `skills/*/SKILL.md` (excluding `skills/layton/`)
- [x] 2.4 Implement `add_skill()` function to create skill file from template
- [x] 2.5 Add skill template constant with Commands, What to Extract, Key Metrics sections
- [x] 2.6 Add error handling for `SKILL_EXISTS` when skill file already exists

## 3. Workflow System CLI (`laytonlib/workflows.py`)

- [x] 3.1 Create `workflows.py` module with workflow file parsing (YAML frontmatter extraction)
- [x] 3.2 Implement `list_workflows()` function to scan `.layton/workflows/` directory
- [x] 3.3 Implement `add_workflow()` function to create workflow file from template
- [x] 3.4 Add workflow template constant with Objective, Steps, Context Adaptation, Success Criteria sections
- [x] 3.5 Add error handling for `WORKFLOW_EXISTS` when workflow file already exists

## 4. CLI Integration (`laytonlib/cli.py`)

- [x] 4.1 Add `skills` command group with list subcommand (default)
- [x] 4.2 Add `skills --discover` flag for skill discovery
- [x] 4.3 Add `skills add <name>` subcommand for skill creation
- [x] 4.4 Add `workflows` command group with list subcommand (default)
- [x] 4.5 Add `workflows add <name>` subcommand for workflow creation
- [x] 4.6 Modify no-arg behavior to return orientation JSON (doctor + skills + workflows)
- [x] 4.7 Add `next_steps` to orientation output with contextual suggestions

## 5. Tests (following existing pattern in `tests/layton/`)

### Unit Tests (`tests/layton/unit/`)

- [x] 5.1 Create `test_skills.py` with tests for:
  - `parse_skill_frontmatter()` - valid/invalid YAML extraction
  - `list_skills()` - empty dir, multiple skills, missing dir
  - `discover_skills()` - finds skills, excludes layton, extracts metadata
  - `add_skill()` - creates file, SKILL_EXISTS error
- [x] 5.2 Create `test_workflows.py` with tests for:
  - `parse_workflow_frontmatter()` - valid/invalid YAML extraction
  - `list_workflows()` - empty dir, multiple workflows, missing dir
  - `add_workflow()` - creates file, WORKFLOW_EXISTS error

### E2E Tests (`tests/layton/e2e/`)

- [x] 5.3 Create `test_skills_e2e.py` with tests for:
  - `layton skills` - JSON output, empty skills, populated skills
  - `layton skills --discover` - finds skills, reports known/unknown
  - `layton skills add <name>` - creates file, error if exists
- [x] 5.4 Create `test_workflows_e2e.py` with tests for:
  - `layton workflows` - JSON output, empty workflows, populated workflows
  - `layton workflows add <name>` - creates file, error if exists
- [x] 5.5 Update `test_doctor_e2e.py` or create `test_orientation_e2e.py`:
  - `layton` (no args) - returns orientation with checks, skills, workflows

### Test Fixtures (`tests/layton/conftest.py`)

- [x] 5.6 Add `temp_skills_dir` fixture for isolated `.layton/skills/`
- [x] 5.7 Add `temp_workflows_dir` fixture for isolated `.layton/workflows/`
- [x] 5.8 Add `sample_skill_file` fixture with valid skill markdown
- [x] 5.9 Add `sample_workflow_file` fixture with valid workflow markdown

## 6. Setup Workflow (`skills/layton/workflows/setup.md`)

- [x] 6.1 Create `setup.md` workflow in `skills/layton/workflows/`
- [x] 6.2 Define workflow frontmatter (name, description, triggers)
- [x] 6.3 Add steps for gathering user info (name, email, timezone, work hours, work days)
- [x] 6.4 Add step to run `layton skills --discover`
- [x] 6.5 Add step to offer skill file creation for discovered skills
- [x] 6.6 Add persona integration (reference `references/persona.md`)

## 7. Example Workflows (`skills/layton/examples/`)

- [x] 7.1 Create `gather.md` example workflow with skill iteration pattern
- [x] 7.2 Update moved `morning-briefing.md` to match new template format
- [x] 7.3 Create `focus-suggestion.md` example workflow with context adaptation

## 8. First Skill File (`.layton/skills/gtd.md`)

- [x] 8.1 Create `.layton/skills/gtd.md` as reference implementation
- [x] 8.2 Document GTD CLI commands in Commands section
- [x] 8.3 Document key extraction (inbox count, next actions, waiting-for items)
- [x] 8.4 Document key metrics (task counts, age of oldest inbox item)

## 9. SKILL.md Updates

- [x] 9.1 Update `skills/layton/SKILL.md` with new capabilities
- [x] 9.2 Add workflow invocation guidance (how AI should use setup, gather, briefing workflows)
- [x] 9.3 Document skill file discovery and management pattern
