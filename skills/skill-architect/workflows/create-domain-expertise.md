# Workflow: Create a Domain Expertise Skill

<required_reading>
Read first:

1. `references/architecture-patterns.md` — Pattern 3 specifics
2. `references/writing-philosophy.md` — principles that must be in SKILL.md
3. `references/spec-fields.md` — frontmatter requirements
</required_reading>

<process>

Domain expertise skills are comprehensive — they cover the full lifecycle (build → debug → test → optimize → ship), contain exhaustive domain knowledge in `references/`, and can be both invoked directly by users and loaded by other skills (like `create-plans`) for domain knowledge.

This is the most complex skill type. Get the architecture right before writing content.

## Step 1: Define the Domain and Scope

Clarify with the user:

- **Domain:** "macOS apps" vs "macOS apps with SwiftUI specifically"
- **Scope:** Full lifecycle (build → ship) or just a subset?
- **Target location:** `skills/{domain-name}/` in the plugin repo, or `.claude/skills/expertise/{domain-name}/` locally
- **Complementary skills:** Should `create-plans` or similar skills be able to load this for knowledge?

Name convention: verb-noun — `build-macos-apps`, `create-python-games`, `develop-rust-systems`

## Step 2: Identify Workflows

Domain expertise skills cover the full lifecycle. Standard workflows for most domains:

- `build-new.md` — Create from scratch
- `add-feature.md` — Extend existing work
- `debug.md` — Find and fix bugs
- `write-tests.md` — Test for correctness
- `optimize-performance.md` — Profile and speed up
- `ship.md` — Deploy/distribute

Add domain-specific workflows as needed (e.g., `implement-game-mechanic.md` for games, `setup-auth.md` for web apps).

## Step 3: Plan the Reference Structure

Structure references by domain concerns, not by document type:

```
references/
├── architecture.md       — How to structure projects in this domain
├── libraries.md          — Ecosystem overview with when-to-use comparisons
├── patterns.md           — Design patterns specific to this domain
├── testing-debugging.md  — How to verify correctness and debug
├── performance.md        — Optimization strategies
├── deployment.md         — How to ship/distribute
└── anti-patterns.md      — Common mistakes consolidated
```

Add domain-specific references as needed.

## Step 4: Research Phase

**This research must be comprehensive, not superficial.**

For each major library/tool/pattern in the domain:
- Check recency (last updated?)
- Check adoption (actively maintained? community size?)
- Check alternatives (what else exists? when to use each?)
- Check deprecation (is anything being replaced?)

Focus on 2024–2025 sources. Skip articles from before 2023 unless they cover fundamental concepts.

Use Context7 MCP if available:
```
mcp__context7__resolve-library-id: {library-name}
mcp__context7__get-library-docs: {library-id}
```

## Step 5: Use skill-creator to Draft and Iterate

**Use Anthropic's `skill-creator` skill** to draft and iterate all files. Do not write the skill manually if skill-creator is available.

```bash
# Prerequisite check:
ls .claude/skills/skill-creator/SKILL.md 2>/dev/null || echo "NOT FOUND — install skill-creator first"
```

If not found, stop: "Please install skill-creator as a project skill in `.claude/skills/skill-creator/` before proceeding."

Read `.claude/skills/skill-creator/SKILL.md` and hand off:

> "I want to create a domain expertise skill called `{name}`. Domain: {domain}. Target lifecycle: build → debug → test → optimize → ship. Planned workflows: [list]. Planned references: [list]. Research: [findings]. Please help me draft SKILL.md, all workflow files, and all reference files."

skill-creator will draft, run evals, present results, iterate, and optimize the description.

### Only if skill-creator is genuinely unavailable

Follow this file-by-file structure as a fallback:

**SKILL.md (router):**
```yaml
---
name: {domain-name}
description: Build {domain things} from scratch through shipping. Full lifecycle:
  build, debug, test, optimize, ship. Use when the user wants to create, extend,
  debug, or deploy {domain things}, or asks about {domain keywords}.
---

<essential_principles>
## How {This Domain} Works

{Domain-specific principles that always apply — not general advice}
</essential_principles>

<intake>
What would you like to do?
1. Build something new
2. Add a feature
3. Debug an issue
4. Write tests
5. Optimize performance
6. Ship/deploy

**Wait for response before proceeding.**
</intake>

<routing>
[map responses to workflows]
</routing>

<reference_index>
[organized by domain area]
</reference_index>

<workflows_index>
[all workflow files]
</workflows_index>
```

**Each reference file** must include:
- Multiple options (not just one library)
- Decision guidance: "If X, use Y. If Z, use A."
- Real working code examples (not pseudocode)
- Trade-offs and anti-patterns
- Current version information

**Each workflow file** must include:
- `<required_reading>` listing specific references to load
- Actual implementation steps (not just "read the references")
- Verification steps
- `<success_criteria>` that are checkable

## Step 6: Completeness Check

Ask: "Could a user build a professional {domain thing} from scratch through shipping using only this skill?"

Must answer YES to:
- [ ] All major libraries/frameworks covered with comparison guidance?
- [ ] All architectural approaches documented?
- [ ] Full lifecycle: build → debug → test → optimize → ship?
- [ ] Platform-specific considerations included?
- [ ] "When to use X vs Y" decision guidance throughout?
- [ ] Common pitfalls documented?
- [ ] Workflows execute real tasks (not just reference knowledge)?
- [ ] Each workflow specifies which references to read?

## Step 7: Validate

```bash
skills-ref validate {skill-path}
```

Also test both use cases:
- **Direct invocation:** Invoke the skill with "Build a new {thing}" — does it route correctly and produce useful output?
- **Knowledge reference:** Can another skill read `references/architecture.md` and get actionable decision guidance?
</process>

<success_criteria>
Domain expertise skill is complete when:

- [ ] Domain and scope clearly defined
- [ ] All lifecycle workflows present (build, debug, test, optimize, ship)
- [ ] References cover domain exhaustively with decision guidance
- [ ] Essential principles inline in SKILL.md (always loaded)
- [ ] `skills-ref validate` passes
- [ ] Passes dual-purpose test: direct invocation + knowledge reference use case
- [ ] Description is trigger-optimized (or optimization queued with skill-creator)
</success_criteria>
