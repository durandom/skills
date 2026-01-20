## Why

Layton needs to help users set up and maintain their project instruction files (CLAUDE.md, AGENTS.md). Currently there's no guidance on best practices, no examples to follow, and no way to audit existing files. Users either cargo-cult from other repos or reinvent patterns ad-hoc.

Additionally, the CLI output is too verbose—passing health checks clutter the display when everything is working fine.

## What Changes

- **Compact CLI output**: Suppress passing health checks, show only `✓ N/N checks passed` summary (expand only on failures)
- **Project instructions reference**: Best practices document for CLAUDE.md and AGENTS.md covering separation of concerns, what goes where, anti-patterns
- **Example files**: Genericized templates based on pensieve-rhdh patterns (examples/CLAUDE.md, examples/AGENTS.md)
- **Audit workflow**: On-demand workflow to analyze a target repo's instruction files and suggest improvements
- **Setup integration**: Mention audit workflow during setup for new users
- **Retrospection workflow**: On-demand workflow for post-workflow reflection to identify improvements

## Capabilities

### New Capabilities

- `compact-output`: CLI output formatting that suppresses passing checks and shows summary only
- `project-instructions`: Reference documentation and examples for CLAUDE.md/AGENTS.md best practices
- `audit-workflow`: Workflow to analyze and suggest improvements to project instruction files
- `retrospect-workflow`: Workflow for post-workflow reflection and improvement capture

### Modified Capabilities

- `setup`: Add step mentioning the audit-project-instructions workflow for new users

## Impact

- **CLI**: `laytonlib/` - output formatting for doctor/status commands
- **References**: `references/project-instructions.md` - new file
- **Examples**: `examples/CLAUDE.md`, `examples/AGENTS.md` - new files
- **Workflows**: `workflows/audit-project-instructions.md`, `workflows/retrospect.md` - new files
- **Workflows**: `workflows/setup.md` - minor modification to mention audit workflow
