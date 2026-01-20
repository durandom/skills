## Context

Stage 0 delivered a working CLI with doctor, context, and config commands. The CLI follows an "agent-first" pattern: JSON output by default, human output via `--human` flag. Layton uses Beads for state management (the "notepad") and `.layton/` for configuration (the "filing cabinet").

This design extends Layton to aggregate data from external skills and synthesize that data into useful briefings. The key challenge is doing this **skill-agnostically**—Layton shouldn't have hardcoded knowledge of GTD, PARA, or any specific skill.

**Current state:**

- CLI: `layton doctor`, `layton context`, `layton config`
- Config: `.layton/config.json`
- Beads integration: Verified via doctor
- Workflows: `track-item.md`, `set-focus.md`, `morning-briefing.md` (Stage 0)

**Constraints:**

- Must work with any skill that has a SKILL.md
- AI-driven workflows, not hardcoded logic
- Thin CLI—deterministic operations only

## Goals / Non-Goals

**Goals:**

- Skill-agnostic integration via markdown "skill files"
- User-customizable workflows via `.layton/workflows/`
- Single-command AI orientation (`layton` with no args)
- First working integration with GTD skill

**Non-Goals:**

- Cross-system entity correlation (Stage 4+)
- Automatic recipe learning (Stage 4+)
- Multi-skill aggregation beyond GTD (future)
- Real-time or push-based updates

## Decisions

### Decision 1: Skill files mirror SKILL.md frontmatter

**Choice:** `.layton/skills/*.md` files use YAML frontmatter with `name`, `description`, `source` fields.

**Rationale:** Consistency with existing SKILL.md pattern. The `source` field allows validation that the skill file matches its source.

**Alternatives considered:**

- JSON files: Rejected—harder to include prose instructions for the AI
- YAML-only: Rejected—need markdown body for "how to query" instructions

### Decision 2: Workflows are AI instructions, not code

**Choice:** Workflow files are markdown documents the AI reads and follows, not executable scripts.

**Rationale:**

- Aligns with the "thin CLI" principle
- Allows flexible, context-aware execution
- Users can customize by editing markdown, not code
- Keeps complexity in the AI, not the CLI

**Alternatives considered:**

- Python workflow scripts: Rejected—adds code complexity, harder to customize
- YAML workflow definitions: Rejected—too rigid, can't express nuanced instructions

### Decision 3: Examples directory for workflow templates

**Choice:** Example workflows live in `skills/layton/examples/`, users copy to `.layton/workflows/` to use.

**Rationale:**

- Clear separation: `workflows/` = core skill operations, `examples/` = user-facing patterns
- Users must explicitly opt-in to workflows
- No fallback/override complexity—AI reads from `.layton/workflows/` only

**Alternatives considered:**

- Fallback resolution (user → template): Rejected—adds complexity, unclear which version runs
- Auto-copy on first use: Rejected—surprising behavior, harder to reason about

### Decision 4: No-arg returns full orientation

**Choice:** `layton` (no args) returns doctor checks + skills inventory + workflows inventory in one JSON response.

**Rationale:**

- Single command gives AI everything it needs
- Reduces round-trips during briefing workflows
- Backwards compatible—superset of previous doctor-only output

**Alternatives considered:**

- Separate `layton status` command: Rejected—adds yet another command
- Keep no-arg as doctor-only: Rejected—misses opportunity to provide full context

### Decision 5: Workflow frontmatter includes triggers

**Choice:** Workflow files have `triggers` field listing phrases that activate them (e.g., `["morning", "briefing", "what should I know"]`).

**Rationale:**

- Enables AI to match user intent to appropriate workflow
- Explicit—no guessing which workflow applies
- Searchable via CLI (`layton workflows` can filter by trigger)

**Alternatives considered:**

- AI infers from description only: Rejected—less precise matching
- Regex patterns: Rejected—overkill, natural language triggers work fine

### Decision 6: Skill files document commands, not parse output

**Choice:** `.layton/skills/gtd.md` contains the commands to run and what to look for, not parsers.

**Rationale:**

- AI interprets human-readable output naturally
- No brittle parsing code
- Works even if skill CLI changes output format slightly

**Alternatives considered:**

- Structured output parsers: Rejected—requires skills to expose `--json` (they may not)
- Screen-scraping adapters: Rejected—fragile, maintenance burden

## Risks / Trade-offs

**Risk: AI misinterprets skill output**
→ Mitigation: Skill files include "What to extract" section with explicit guidance

**Risk: Workflow proliferation**
→ Mitigation: Start with 3 core examples; users add more only if needed

**Risk: Discovery finds skills Layton can't use**
→ Mitigation: Discovery reports unknown skills; user decides whether to create skill file

**Trade-off: No fallback for workflows**
→ Accepted: Simpler mental model. Users must explicitly add workflows they want.

**Trade-off: AI-dependent execution**
→ Accepted: Core design philosophy. Deterministic operations stay in CLI, intelligence stays in AI.

## File Structure

```
skills/layton/
├── SKILL.md                    # Updated with new capabilities
├── laytonlib/
│   ├── cli.py                  # Extended with skills/workflows commands
│   ├── skills.py               # NEW: Skill discovery and management
│   └── workflows.py            # NEW: Workflow listing
├── workflows/
│   ├── setup.md                # NEW: Interactive onboarding
│   ├── track-item.md           # Stage 0 (core operation)
│   └── set-focus.md            # Stage 0 (core operation)
├── examples/                   # NEW
│   ├── gather.md               # NEW
│   ├── morning-briefing.md     # MOVED from workflows/
│   └── focus-suggestion.md     # NEW
└── references/
    └── ...

.layton/
├── config.json                 # Stage 0
├── skills/                     # NEW
│   └── gtd.md                  # First skill file
└── workflows/                  # NEW (empty initially)
```

## Migration

**Stage 0 → Stage 1 migration:**

- Move `skills/layton/workflows/morning-briefing.md` → `skills/layton/examples/morning-briefing.md`
- Reason: `morning-briefing.md` is a user-facing workflow pattern, not a core skill operation
- Core operations (`track-item`, `set-focus`) stay in `workflows/` as they're internal skill mechanics

### Decision 7: Add commands bootstrap from templates

**Choice:** `layton skills add <name>` and `layton workflows add <name>` create new files from templates, not copy existing examples.

**Rationale:**

- Consistent pattern for both skills and workflows
- Examples are reference material, not copy targets
- Templates ensure correct structure (frontmatter, sections)
- Users learn the format by filling in the template

**Templates needed:**

- Skill template: frontmatter (`name`, `description`, `source`) + sections (Commands, What to Extract)
- Workflow template: frontmatter (`name`, `description`, `triggers`) + sections (Steps, Success Criteria)

## Open Questions

1. **How to handle skill file staleness?**
   - If source SKILL.md changes significantly, skill file may be outdated
   - Option: `layton skills check` command that compares against source
