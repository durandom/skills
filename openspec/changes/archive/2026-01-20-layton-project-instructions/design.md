## Context

Layton is an orchestration skill that helps users manage attention across multiple integrated skills. It currently outputs verbose health check results even when everything passes. Users setting up Layton in new repos have no guidance on how to structure their CLAUDE.md and AGENTS.md files.

The pensieve-rhdh repo demonstrates good patterns:

- CLAUDE.md: Human-readable context (what the repo is, how to work here, entry points)
- AGENTS.md: Mechanical rules for agents (quick refs, session completion protocol)
- Separation of concerns with minimal overlap

## Goals / Non-Goals

**Goals:**

- Provide best-practice guidance for project instruction files
- Give users concrete examples to adapt (not copy-paste templates)
- Enable auditing existing files against best practices
- Support continuous improvement through workflow retrospection
- Reduce noise in CLI output when everything is healthy

**Non-Goals:**

- Auto-generating CLAUDE.md/AGENTS.md (users should understand and customize)
- Enforcing any particular structure (guidance, not rules)
- Complex CLI formatting or theming
- Integration with external documentation systems

## Decisions

### 1. Examples over Templates

**Decision**: Put genericized examples in `examples/` rather than rigid templates in `templates/`.

**Rationale**:

- Templates imply "fill in the blanks" which leads to cargo-culting
- Examples show patterns to understand and adapt
- Consistent with existing Layton pattern (examples/ vs workflows/)

**Alternatives considered**:

- Templates with placeholders: Too prescriptive, less educational
- No examples, just reference doc: Harder to learn from

### 2. Reference Doc Structure

**Decision**: Single `references/project-instructions.md` covering both files with clear separation.

**Rationale**:

- CLAUDE.md and AGENTS.md are related; discussing together clarifies separation of concerns
- Avoids file proliferation in references/
- Can include anti-patterns and "what goes where" guidance

**Alternatives considered**:

- Separate refs for each file: Harder to show relationships
- Inline in SKILL.md: Too long, clutters skill definition

### 3. Audit Workflow Design

**Decision**: Read-only analysis workflow that suggests but never auto-applies changes.

**Rationale**:

- Project instructions are deeply personal/contextual
- Users should understand why changes are suggested
- Avoid breaking existing setups

**Workflow steps**:

1. Read target repo's CLAUDE.md and AGENTS.md (or note if missing)
2. Load reference doc for comparison criteria
3. Analyze against best practices (verbosity, duplication, missing sections)
4. Present findings as suggestions with rationale
5. User decides what to apply

### 4. Compact Output Implementation

**Decision**: Summary line for passing checks (`✓ N/N checks passed`), expand only on failure.

**Rationale**:

- Green path should be quiet
- Failures need detail for debugging
- Matches Unix philosophy (no news is good news)

**Implementation**:

- Modify `laytonlib/` output formatting
- Add `--verbose` flag to force full output if needed

### 5. Retrospect Workflow Scope

**Decision**: Generic post-workflow reflection, not tied to specific workflows.

**Rationale**:

- Any workflow can benefit from reflection
- Keep it simple: what worked, what didn't, what to change
- User explicitly invokes (not auto-triggered)

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Examples become stale as patterns evolve | Reference doc captures principles; examples are illustrative |
| Audit workflow is too opinionated | Frame suggestions as "consider" not "must"; show rationale |
| Compact output hides useful info | Add `--verbose` flag; show full output on any failure |
| Retrospect workflow rarely used | Mention in SKILL.md; eventually auto-suggest after workflows |

## Open Questions

- Should the audit workflow check for integration hooks (e.g., Layton auto-invoke in CLAUDE.md)?
- Should examples include variants for different repo types (code vs knowledge base)?
