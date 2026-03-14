---
name: cass
description: >
  Searches, indexes, and exports Claude Code sessions using the cass CLI (Coding Agent Session
  Search). Use when the user wants to find past sessions, search conversation history, look up
  prior work on a topic, export a session to markdown, discover related sessions for a file, or
  check session activity timelines. Triggers on: "search my sessions", "find past work on X",
  "export session", "look in my history", "what sessions do I have about", "find related sessions",
  "when did I work on".
---

<objective>
Help the user search, explore, and export their Claude Code sessions using the `cass` CLI.
</objective>

<quick_start>
1. Check index freshness: `cass status --json`
2. If stale (recommended_action = "index"), run: `cass index`
3. Execute the user's request (search / export / context / timeline)
</quick_start>

<process>

## Step 1: Pre-flight Check

Always run this first:

```bash
cass status --json
```

Key fields to check:
- `recommended_action`: `"ok"` = index is fresh; `"index"` = needs reindexing
- `db_stats.total_sessions`: how many sessions are indexed
- `freshness.stale`: true if index is stale

If stale, run:

```bash
cass index
```

Skip re-indexing if the user is searching a session they already know the path to (direct export).

---

## Step 2: Execute the Request

### Search sessions

```bash
# Basic search
cass search "topic keyword" --json --fields summary

# Limit to current workspace
cass search "keyword" --json --fields summary --workspace $(pwd)

# Filter by time
cass search "keyword" --json --fields summary --days 7

# Filter by agent (claude_code, cursor, codex, aider, etc.)
cass search "keyword" --json --fields summary --agent claude_code

# Chained search (narrow down results)
cass search "first topic" --robot-format sessions | cass search "second topic" --sessions-from -
```

Output fields in `--fields summary`: `source_path`, `line_number`, `agent`, `title`, `score`.

### Export a session

```bash
# Export to stdout (review inline)
cass export ~/.claude/projects/<encoded-path>/<session-id>.jsonl

# Export to file
cass export <path-to-session.jsonl> -o /tmp/session.md

# Include tool call details
cass export <path> --include-tools
```

Session files live at: `~/.claude/projects/<workspace-encoded>/` — encode workspace path by replacing `/` with `-`.

### Find related sessions for a file

```bash
cass context <path-to-session.jsonl> --json --limit 5
```

Returns sessions that worked in the same workspace or touched the same files.

### View activity timeline

```bash
# Last 7 days
cass timeline --days 7

# Specific range
cass timeline --since 2025-01-01 --until 2025-01-31
```

### Expand context around a search result

When `cass search` returns a `line_number`, use `expand` to see surrounding messages:

```bash
cass expand <path-to-session.jsonl> --line <line_number>
```

---

## Step 3: Present Results

**For search results:** Show session title + path. If the user wants details, export the most relevant session.

**For exports:** Render the markdown inline or summarize key decisions/actions from the session.

**For context results:** List related sessions with their titles and workspaces.

---

## Tips

- Use `--fields summary` to keep token usage low for search results.
- Use `--workspace $(pwd)` to scope to the current project.
- `cass search --robot-format sessions` outputs paths only — useful for piping into export or chained searches.
- For semantic search (finds conceptually related content): `cass search "topic" --mode semantic`
- Session paths follow this pattern: `~/.claude/projects/<dir-path-with-dashes>/<uuid>.jsonl`

</process>

<success_criteria>
Session search/exploration is complete when:

- [ ] Index freshness verified (and refreshed if needed)
- [ ] User's sessions found or confirmed absent
- [ ] Relevant session content surfaced (exported/expanded as needed)
</success_criteria>
