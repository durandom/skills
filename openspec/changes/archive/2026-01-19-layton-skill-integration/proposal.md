## Why

Stage 0 established Layton's foundation (doctor, context, config) but Layton can't yet do useful work. To deliver on the "personal secretary" vision, Layton needs to aggregate data from external skills (like GTD) and synthesize briefings. This requires a skill-agnostic integration layer—Layton learns how to work with skills through markdown "skill files" rather than hardcoded integrations.

## What Changes

- **New directory**: `.layton/skills/` for skill inventory (how Layton interacts with each skill)
- **New directory**: `.layton/workflows/` for user-customizable AI workflows (gather, briefings, focus)
- **Modified CLI behavior**:
  - `layton` (no args) - Now returns doctor checks + skills inventory + workflows inventory (AI orientation)
- **New CLI commands**:
  - `layton skills` - List known skills from `.layton/skills/`
  - `layton skills --discover` - Scan `skills/`, diff against known skills
  - `layton skills add <name>` - Bootstrap new skill file from template
  - `layton workflows` - List user workflows from `.layton/workflows/`
  - `layton workflows add <name>` - Bootstrap new workflow file from template
- **New skill workflow** (in `skills/layton/workflows/`):
  - `setup.md` - Interactive onboarding (name, email, timezone, work hours, skill discovery)
- **Example workflows** (in `skills/layton/examples/`):
  - `gather.md` - Aggregate data from all known skills
  - `morning-briefing.md` - Morning briefing synthesis
  - `focus-suggestion.md` - Focus recommendation
  - These are reference patterns to learn from, not copy targets
- **User workflows** (in `.layton/workflows/`):
  - Empty initially; users create with `layton workflows add <name>`
  - AI reads workflows from `.layton/workflows/`
- **First skill file**: `.layton/skills/gtd.md` as template

## Capabilities

### New Capabilities

- `skill-inventory`: Skill file format (YAML frontmatter with name, description, source), template for bootstrapping new skill files, discovery mechanism (scanning `skills/`), and CLI commands for managing known skills
- `workflow-system`: Workflow file format (YAML frontmatter with name, description, triggers), template for bootstrapping new workflows, examples in `skills/layton/examples/` for reference, user workflows in `.layton/workflows/`, CLI for listing and adding workflows
- `setup-workflow`: Interactive onboarding workflow (in skill's workflows/) gathering user info (name, email, timezone, work hours, work days), running skill discovery, using `layton config set` to persist
- `gather-workflow`: The gather workflow that reads `.layton/skills/`, executes documented commands, and aggregates results for other workflows to consume
- `briefing-workflow`: Morning briefing workflow combining temporal context, beads state, gathered skill data, and user preferences into synthesized output
- `focus-workflow`: Focus suggestion workflow helping user decide what to work on based on context and available tasks

### Modified Capabilities

- `cli-framework`: No-arg invocation now returns combined output: doctor checks + skills inventory (frontmatter extraction from `.layton/skills/`) + workflows inventory (frontmatter extraction from `.layton/workflows/`). Provides full AI orientation in one call.

## Impact

- **New files**: `.layton/skills/`, `.layton/workflows/` directories and their contents
- **CLI changes**: `layton` (no args) output extended; new `layton skills`, `layton workflows` commands
- **Skill workflows**: `skills/layton/workflows/setup.md` added
- **Example workflows**: `skills/layton/examples/` with gather, morning-briefing, focus-suggestion
- **User workflows**: `.layton/workflows/` starts empty; populated when user copies examples
- **SKILL.md update**: Add workflow invocation guidance to the skill description
- **Dependencies**: Requires GTD skill to be available for first integration
- **Backwards compatible**: No-arg output is extended (superset of previous), not replaced
