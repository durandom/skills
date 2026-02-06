---
description: Research a topic using parallel agents, synthesize findings into a documented artifact
argument-hint: <topic> [--quick | --thorough]
allowed-tools: Read, Write, Bash, Glob, Grep, Task, WebSearch, WebFetch, TodoWrite
model: sonnet
---

<objective>
Research a topic by spawning specialized parallel agents, then synthesize findings into a reusable markdown artifact at `docs/research/YYYY-MM-DD-<topic-slug>.md`.

**Depth modes:**

- `--quick` — Single web-docs agent, fast (~30s), good for "what's the API for X?"
- *(default)* — 3 parallel agents (web-docs + community + codebase), balanced coverage
- `--thorough` — 5 parallel agents + extended synthesis, for major architectural decisions

**Examples:**

- `/research React Server Components` — default depth, parallel agents
- `/research zustand vs jotai --quick` — fast comparison from official docs
- `/research authentication patterns --thorough` — deep dive with all sources
</objective>

<context>
Project root: !`pwd`
Existing research: !`ls docs/research/ 2>/dev/null | head -10 || echo "No existing research"`
Tech stack hints: !`cat package.json 2>/dev/null | grep -E '"(dependencies|devDependencies)"' -A 20 | head -25 || echo "No package.json"`
</context>

<process>

## 1. Parse Arguments

Extract from `$ARGUMENTS`:

- **topic**: The research subject (required)
- **depth**: `--quick`, `--thorough`, or default (standard)

If topic is empty, use AskUserQuestion to get it.

## 2. Prepare Output Path

```bash
# Generate slug and date
DATE=$(date +%Y-%m-%d)
SLUG=$(echo "<topic>" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
OUTPUT="docs/research/${DATE}-${SLUG}.md"

# Ensure directory exists
mkdir -p docs/research
```

## 3. Spawn Research Agents

Based on depth, spawn agents **in parallel** using the Task tool. All agents in a single message.

### Quick Mode (1 agent)

Spawn only the **web-docs-researcher** agent:

```
Task tool:
- subagent_type: "general-purpose"
- model: "haiku"
- prompt: [See web-docs-researcher prompt below]
```

### Standard Mode (3 agents in parallel)

Spawn ALL THREE agents in a **single message** with multiple Task tool calls:

1. **web-docs-researcher** (haiku) — Official docs, GitHub READMEs, release notes
2. **community-researcher** (haiku) — Stack Overflow, Reddit, Discord, blog posts
3. **codebase-researcher** (haiku) — Local patterns, existing implementations, conventions

### Thorough Mode (5 agents in parallel)

Spawn all three above PLUS:

1. **package-researcher** (haiku) — npm/PyPI analysis, alternatives, bundle size, maintenance
2. **academic-researcher** (haiku) — arXiv, papers, research foundations (if relevant)

---

## Agent Prompts

### web-docs-researcher

```
Research "<topic>" using ONLY official documentation and authoritative sources.

**Your focus:**
- Official documentation and getting started guides
- GitHub repository READMEs and wikis
- Release notes and changelogs
- Official blog posts and announcements

**Tools available:** WebSearch, WebFetch

**Process:**
1. Search for official documentation
2. Fetch and read key pages
3. Extract: core concepts, API patterns, setup requirements, gotchas

**Return JSON:**
{
  "source_type": "official_docs",
  "findings": [
    {"title": "...", "url": "...", "summary": "...", "relevance": "high|medium"}
  ],
  "key_concepts": ["..."],
  "code_examples": ["..."],
  "gotchas": ["..."],
  "confidence": "high|medium|low"
}
```

### community-researcher

```
Research "<topic>" using community sources and real-world experiences.

**Your focus:**
- Stack Overflow questions and accepted answers
- Reddit discussions (r/programming, r/webdev, etc.)
- Dev.to, Medium, Hashnode blog posts
- GitHub issues and discussions
- Discord/forum threads

**Tools available:** WebSearch, WebFetch

**Process:**
1. Search for common problems and solutions
2. Look for "X vs Y" comparisons if relevant
3. Find real-world pitfalls and workarounds

**Return JSON:**
{
  "source_type": "community",
  "findings": [
    {"title": "...", "url": "...", "summary": "...", "sentiment": "positive|negative|mixed"}
  ],
  "common_problems": ["..."],
  "workarounds": ["..."],
  "community_sentiment": "...",
  "confidence": "high|medium|low"
}
```

### codebase-researcher

```
Research how "<topic>" relates to THIS codebase. Find existing patterns and conventions.

**Your focus:**
- Similar implementations already in the codebase
- Existing patterns that should be followed
- Dependencies already installed that relate to the topic
- Configuration or conventions that would affect implementation

**Tools available:** Glob, Grep, Read

**Process:**
1. Search for related keywords in the codebase
2. Check package.json/requirements.txt for related dependencies
3. Look for similar patterns or prior art
4. Identify conventions (naming, structure, error handling)

**Return JSON:**
{
  "source_type": "codebase",
  "existing_patterns": [
    {"file": "...", "line": "...", "description": "..."}
  ],
  "related_dependencies": ["..."],
  "conventions": ["..."],
  "suggested_location": "...",
  "confidence": "high|medium|low"
}
```

### package-researcher (thorough only)

```
Research "<topic>" from a package/dependency perspective.

**Your focus:**
- Package registry details (npm, PyPI, crates.io)
- Bundle size and performance impact
- Maintenance status (last update, open issues, contributors)
- Alternative packages and comparisons
- Security advisories

**Tools available:** WebSearch, WebFetch

**Return JSON:**
{
  "source_type": "packages",
  "packages": [
    {"name": "...", "version": "...", "weekly_downloads": "...", "last_updated": "...", "bundle_size": "..."}
  ],
  "recommendation": "...",
  "alternatives": ["..."],
  "security_notes": ["..."],
  "confidence": "high|medium|low"
}
```

### academic-researcher (thorough only)

```
Research "<topic>" for academic foundations and research papers.

**Your focus:**
- arXiv papers on algorithms or approaches
- Research that influenced the technology
- Theoretical foundations
- Benchmarks and performance studies

**Tools available:** WebSearch, WebFetch

**Return JSON:**
{
  "source_type": "academic",
  "papers": [
    {"title": "...", "authors": "...", "year": "...", "key_insight": "..."}
  ],
  "theoretical_foundations": ["..."],
  "confidence": "high|medium|low"
}
```

---

## 4. Collect and Synthesize Results

After all agents complete:

1. **Parse JSON results** from each agent
2. **Deduplicate** findings across sources
3. **Identify conflicts** (community says X, docs say Y)
4. **Calculate overall confidence** (weighted average)
5. **Generate recommendation** based on codebase context

## 5. Write Research Artifact

Write to `docs/research/YYYY-MM-DD-<topic-slug>.md`:

```markdown
# Research: <topic>

> Generated: YYYY-MM-DD HH:MM | Depth: quick|standard|thorough | Confidence: HIGH/MEDIUM/LOW

## TL;DR

[2-3 sentence recommendation based on ALL findings, grounded in codebase context]

## Problem Statement

[What we're trying to understand or decide]

## Key Findings

### Official Documentation
[Synthesized from web-docs-researcher]
- ...

### Community Insights
[Synthesized from community-researcher]
- ...

### Codebase Patterns
[Synthesized from codebase-researcher]
- Existing pattern at `path/to/file.ts:42`: ...
- Convention: ...

### Package Analysis (if thorough)
[Synthesized from package-researcher]

### Academic Foundations (if thorough)
[Synthesized from academic-researcher]

## Recommended Approach

[Concrete recommendation with rationale]

1. Step one...
2. Step two...

## Code Example

```<lang>
// Example implementation based on findings
```

## Trade-offs

| Option | Pros | Cons |
|--------|------|------|
| A | ... | ... |
| B | ... | ... |

## Open Questions

- [ ] Question that couldn't be answered...
- [ ] Decision that needs user input...

## Sources

- [Title](url) — relevance note
- [Title](url) — relevance note
- `path/to/local/file.ts` — existing pattern

```

## 6. Report Completion

```

Research complete: docs/research/YYYY-MM-DD-<topic-slug>.md

**TL;DR:** [one-liner recommendation]
**Confidence:** HIGH/MEDIUM/LOW
**Sources:** X official, Y community, Z codebase patterns

Open questions: [count] (see document)

```

</process>

<confidence_levels>

- **HIGH**: Multiple authoritative sources agree, codebase patterns clear, no conflicts
- **MEDIUM**: Some sources agree, minor conflicts resolved, some assumptions made
- **LOW**: Sources conflict, limited information found, significant uncertainty

If confidence is LOW, use AskUserQuestion:
- header: "Low Confidence"
- question: "Research confidence is LOW because [reason]. How to proceed?"
- options:
  - "Dig deeper" — Run thorough mode or additional searches
  - "Accept uncertainty" — Proceed with caveats documented
  - "Ask me specific questions" — Clarify what's unclear

</confidence_levels>

<success_criteria>

- All agents completed (or timed out with partial results)
- Findings synthesized without hallucination (only report what agents found)
- Codebase context incorporated into recommendation
- Artifact written to docs/research/
- Confidence level honestly assessed
- Sources linked and attributed

</success_criteria>
