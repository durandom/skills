# Workflow: Explore Code Map

<objective>
Navigate an existing code map to understand a codebase before starting work.

Use this workflow when:

- Starting a new task in an unfamiliar codebase
- Needing to find relevant entry points for a feature
- Building a mental model of system architecture
</objective>

<required_reading>
@.claude/skills/code-map/references/format-spec.md
</required_reading>

<process>

## Step 1: Check for Map

Verify a code map exists:

```bash
ls docs/map/MAP.md 2>/dev/null || echo "NO_MAP"
```

**If NO_MAP:**

- Inform user: "No code map found at docs/map/"
- Offer to create one: "Run /code-map create to generate a map for this codebase"
- STOP workflow

**If map exists:** Continue to Step 2.

## Step 2: Read Entry Point

Read the map index:

```bash
cat docs/map/MAP.md
```

Note:

- Available domains (from Domains Index table)
- Code statistics (files, languages, last updated)
- Quick start commands for grep navigation

## Step 3: Read Architecture (L0)

Read the system overview:

```bash
cat docs/map/ARCHITECTURE.md
```

Note:

- System purpose and boundaries
- Technology stack (languages, frameworks, key libraries)
- High-level architecture diagram
- Domain map (all major subsystems)
- Main entry points (CLI commands, API endpoints, key classes)

**Build mental model:**

- What does this system do?
- What are its main components?
- How do they connect?

## Step 4: Identify Relevant Domains

Based on the user's task, identify which L1 domains matter.

**Finding domains:**

```bash
# List all domains
grep -r "\[L1:" docs/map/domains/

# Read a specific domain
cat docs/map/domains/{domain-name}.md
```

**Domain selection heuristic:**

- Task mentions specific feature? Find domain that owns it
- Task is cross-cutting? May need multiple domains
- Unclear? Start with domain closest to entry point

**For each relevant domain, note:**

- Entry points with code links
- Dependencies on other domains
- Key files to examine

## Step 5: Report Exploration Findings

Summarize understanding to the user:

**Report template:**

```
## Codebase Understanding

**System:** [one-line purpose]
**Stack:** [key technologies]

**Relevant Domains:**
- [Domain 1]: [why relevant]
- [Domain 2]: [why relevant]

**Entry Points for Task:**
- `[function/class](path/to/file.py#L42)` - [what it does]
- `[function/class](path/to/file.py#L87)` - [what it does]

**Suggested Starting Point:** [file/function to start with]

**Questions:**
- [Any clarifications needed before proceeding?]
```

</process>

<success_criteria>

- Agent can describe codebase purpose in one sentence
- Agent has identified which files are relevant to the task
- Agent has located specific entry points (function/class with line numbers)
- Agent can explain how relevant domains connect
- Agent asks clarifying questions if task scope is unclear
</success_criteria>

<tips>

**Speed optimization:**

- If task is narrow, skip L0 after first visit - jump directly to L1
- Use grep anchors: `grep -A 50 "\[L1:auth\]" docs/map/domains/auth.md`
- Cache mental model across sessions (agent memory)

**When map is stale:**

- Code links have wrong line numbers? Validation script should catch this
- Missing recent files? Suggest running /code-map validate

**When map doesn't cover task:**

- Domain missing? User may need to add L1 doc
- Too high-level? May need L2 module docs
- Inform user and suggest update

</tips>
