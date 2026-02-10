---
name: the-day
description: Generate daily overview (TODAY.md) with calendar, tasks, weather, and motivational content. Use for morning planning, day organization, daily review, or generating today's schedule.
---

<objective>
Generate a comprehensive daily overview document (TODAY.md) with calendar, tasks, weather, and motivational content, then interactively plan the day with time-blocked calendar entries.
</objective>

<essential_principles>

## Day CLI

All deterministic operations go through the `day` CLI. Run from **repo root**:

```bash
# Check current status
./skills/the-day/scripts/day

# Archive existing TODAY.md
./skills/the-day/scripts/day archive --force

# Format GTD tasks as markdown
./skills/the-day/scripts/day format-gtd

# Generate TODAY.md (deterministic parts only)
./skills/the-day/scripts/day generate --force
```

## What's Deterministic vs AI-Driven

| Component | Handler | Notes |
|-----------|---------|-------|
| Archive TODAY.md | CLI | `day archive --force` |
| GTD task formatting | CLI | `day format-gtd` |
| Template rendering | CLI | `day generate --force` |
| Calendar events | MCP + AI | Format with emojis |
| Weather | WebSearch + AI | Interpret conditions |
| Starred emails | MCP + AI | Categorize by type |
| Inspiration | AI | Quote + ASCII art |
| Wikipedia summary | WebSearch + AI | Leadership lesson |
| Interactive planning | AI | AskUserQuestion |

## User Context

Defaults (override in CLAUDE.md or project config):

- Location: Kiel, Germany
- Timezone: Europe/Berlin
- Email: configured in Google Workspace MCP

</essential_principles>

<process>

## Phase 1: Archive & Status

1. **Check current status:**

   ```bash
   ./skills/the-day/scripts/day
   ```

   Shows: TODAY.md status, GTD task count, next-step hints.

2. **Archive existing TODAY.md (if exists):**

   ```bash
   ./skills/the-day/scripts/day archive --force
   ```

   Moves to `logs/today/YYYY-MM-DD-HHMM.md`.

## Phase 2: Gather Context

1. **Fetch weather data (AI):**
   - Use WebSearch for current conditions in user's location
   - **Metric units only**: °C, km/h
   - **AI interprets:** "Bundle up! Cold morning..." or "Perfect day for outdoor work!"

2. **Retrieve calendar events (MCP + AI):**
   - Use `mcp__google_workspace__get_events` for today
   - Format with `day format-calendar` or manually with emojis
   - Time-ordered (all-day first, then chronological)

3. **Get GTD tasks (CLI):**

   ```bash
   ./skills/the-day/scripts/day format-gtd
   ```

   Returns grouped markdown: Focus (High/Low Energy), Async, Meetings.

4. **Gather starred emails (MCP + AI):**
   - Search: `mcp__google_workspace__search_gmail_messages` query="is:starred"
   - **AI categorizes:** ACTION REQUIRED, Conference, Compliance, Personal
   - Fix URLs: replace `u/0/` with `u/1/`

5. **Generate inspiration (AI):**
   - Use WebSearch for Wikipedia featured article of the day
   - Create ASCII art banner
   - Generate inspiring quote
   - Summarize article with leadership lesson

## Phase 3: Generate TODAY.md

1. **Generate base document (CLI):**

   ```bash
   ./skills/the-day/scripts/day generate --force
   ```

   Fills: DATE_FULL, TIME, LOCATION, GTD_TASKS.
   Leaves placeholders: WEATHER_CONTENT, CALENDAR_EVENTS, STARRED_EMAILS, INSPIRATION, WIKIPEDIA_ARTICLE.

2. **Fill AI placeholders (AI):**
   - Read generated TODAY.md
   - Replace remaining `{{PLACEHOLDER}}` with gathered content
   - Write updated file

## Phase 4: Interactive Planning

1. **Identify available time slots:**
   - Analyze calendar events
   - Find free blocks between meetings
   - Show: "09:00-10:30 (1.5h)", "14:00-16:00 (2h)"

2. **Review tasks for scheduling:**
   - Present high-priority GTD tasks
   - Use AskUserQuestion: "Which tasks to schedule?"
   - Suggest slots based on energy levels

3. **Create calendar entries (MCP):**
   - Use `mcp__google_workspace__create_event`
   - Settings: `transparency="transparent"`, `visibility="private"`
   - Format: "🎯 #42 - Task Title" or "📧 Process Starred Emails"

4. **Update TODAY.md with final calendar:**
   - Re-fetch events (now includes work blocks)
   - Update calendar section
   - Mark work blocks with ⭐

</process>

<success_criteria>

- TODAY.md created with all sections populated
- Weather in metric units with interpretation
- Calendar events formatted with emojis and links
- GTD tasks grouped by energy/context (via CLI)
- Starred emails categorized
- Interactive planning completed with user approval
- Calendar events created with privacy settings
- Previous TODAY.md archived (if existed)

</success_criteria>

<notes>

## CLI-First Philosophy

```
day status        → Overview + hints
day archive       → Archive to logs/
day format-gtd    → GTD → markdown
day generate      → Template → TODAY.md (deterministic parts)
AI workflow       → Fill remaining placeholders
```

## JSON Output

All CLI commands support `--json` for structured output:

```bash
./skills/the-day/scripts/day --json
./skills/the-day/scripts/day format-gtd --json
```

## Gmail URL Fix

User has multiple Google accounts. MCP returns `u/0/` in links.
**Always replace `u/0/` with `u/1/`** for correct account access.

## TODAY.md as Source of Truth

- Read by `/focus` command to avoid redundant API calls
- Updated by `/focus` to track progress: "✅ HH:MM - [Completed work]"

</notes>
