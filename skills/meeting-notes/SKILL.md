---
name: meeting-notes
description: This skill should be used when the user asks to "sync my meeting notes", "sync meeting notes", "update meeting notes", "check for new meeting transcripts", "manage meeting tags", "list meeting tags", or "add a meeting tag". Handles syncing Google Calendar meetings with Gemini transcripts, organizing them into the meetings directory, and managing tag definitions.
metadata:
  version: "2.1.0"
---

# Meeting Notes Sync

Sync and manage meeting transcripts from Google Calendar and Gemini email notes using the meeting_notes automation tool.

**Script location:** `scripts/meeting_notes` **relative to this SKILL.md file** (not the working directory).
Derive the absolute script path from this file's location:

- If this SKILL.md is at `/path/to/meeting-notes/SKILL.md`
- Then the script is at `/path/to/meeting-notes/scripts/meeting_notes`

**⚠️ INTERACTIVE SKILL:** This skill requires user approval at each step. Never auto-execute `decide` or `download` commands without explicit user confirmation.

## AI Agent Usage

**IMPORTANT: When calling this script from an AI agent context:**

- **Always use the `--json` flag** for machine-readable output
- **Flag order matters:** `--json` is a global flag and MUST come BEFORE the command
- JSON output includes structured data with `next_steps`, `decision_table`, and `pending_decisions`
- Parse JSON to determine workflow state and present information to users
- When proposing meeting classifications:
  - Use the `AskUserQuestion` tool (never just text)
  - Make intelligent groupings and proposals based on meeting patterns
  - Group meetings by detected patterns (e.g., "All 1:1s → one-on-ones,r", "Team meetings → team,r")
  - Highlight anomalies or meetings that need special attention
  - Provide clear, actionable options with descriptions of what each choice does

**Example AI workflow:**

```bash
# CORRECT: --json before command
scripts/meeting_notes --json status
scripts/meeting_notes --json decide
scripts/meeting_notes --json download

# INCORRECT: --json after command
scripts/meeting_notes status --json  # ❌ Won't work!

# Complete workflow:
# 1. Get status as JSON
scripts/meeting_notes --json status

# 2. Parse JSON to check pending_decisions_count
# 3. If pending, use decision_table to analyze patterns
# 4. Use AskUserQuestion to present grouped proposals
# 5. Execute decisions based on user choice
scripts/meeting_notes decide --accept-all  # Execute (no need for --json on actions)

# 6. Verify completion
scripts/meeting_notes --json status
```

## Purpose

This skill automates the process of discovering calendar meetings, matching them with Gemini-generated transcripts and summaries, and organizing everything into a structured directory hierarchy within the pensieve repository.

## When to Use

Use this skill when:

- Syncing meeting notes since the last sync
- Checking for new Gemini transcripts
- Organizing meeting transcripts and summaries
- Setting up recurring vs one-off meeting classifications
- Managing tag definitions (creating, editing, renaming tags)

## How It Works

The meeting notes sync runs a three-phase workflow:

### Phase 1: Sync (Discovery + Matching)

Discover calendar events and match with Gemini emails in a single step.

```bash
scripts/meeting_notes sync
```

This command:

- Fetches calendar events since the last sync
- Searches for corresponding Gemini transcript/summary emails
- Matches bidirectionally (calendar → emails and orphaned emails → meetings)
- Generates slugs for new meetings
- Suggests recurring/one-off classification and tags
- Outputs a decision table showing meetings that need classification

### Phase 2: Decide (Classification)

Apply recurring and tag decisions to meetings.

**Accept all suggestions:**

```bash
scripts/meeting_notes decide --accept-all
```

**Override specific meetings, then accept the rest (recommended for small changes):**

```bash
# Step 1: Override only the meetings you disagree with
scripts/meeting_notes decide 7=rhdh,r 13=one-on-ones,r

# Step 2: Accept all remaining suggestions
scripts/meeting_notes decide --accept-all
```

This two-step approach is ideal when you want to change only a few meetings out of many. The first `decide` overrides specific meetings, and the second `decide --accept-all` applies suggestions to all meetings that haven't been decided yet.

**Inline syntax (for complete manual control):**

```bash
scripts/meeting_notes decide 1=rhdh,r 2=team,o 3=one-on-ones,r
```

Format: `[number]=[tag],[r|o]`

- `r` = recurring
- `o` = one-off

**Grouped syntax:**

```bash
scripts/meeting_notes decide --tag 1=rhdh,2=team --recurring 1,3 --one-off 2
```

This command:

- Classifies meetings as recurring or one-off
- Assigns tags for organization (rhdh, one-on-ones, team, planning, etc.)
- Generates directory paths based on classification
- Saves recurring patterns to state for future syncs
- Can be run multiple times - each run updates only the specified meetings

### Phase 3: Download (Asset Retrieval)

Download transcripts, summaries, and attachments.

```bash
scripts/meeting_notes download
```

This command:

- Downloads Gemini transcripts and summaries
- Downloads calendar attachments
- Follows links in documents to download referenced materials
- Creates README.md with meeting metadata and summary
- Generates metadata.json for programmatic access

## Directory Structure

Meetings are organized by tag and type:

**Recurring meetings:**

```
meetings/{tag}/{slug}/{date}/
  ├── README.md
  ├── metadata.json
  ├── gemini-transcript.md
  └── gemini-summary.md
```

**One-off meetings:**

```
meetings/{tag}/{date}-{slug}/
  ├── README.md
  ├── metadata.json
  ├── gemini-transcript.md
  └── gemini-summary.md
```

**Common tags:**

- `rhdh` - Red Hat Developer Hub related meetings
- `one-on-ones` - 1:1 meetings
- `team` - Team meetings, standups, syncs
- `planning` - Planning and strategy sessions
- `uncategorized` - Meetings without a specific tag

## Browsing Meetings

Use the `list` and `show` commands to explore synced meetings.

### List Meetings

```bash
# List all meetings (newest first)
scripts/meeting_notes list

# Filter by tag
scripts/meeting_notes list --tag rhdh
scripts/meeting_notes list --tag one-on-ones

# Filter by type
scripts/meeting_notes list --recurring        # recurring only
scripts/meeting_notes list --one-off          # one-off only

# Filter by time range
scripts/meeting_notes list --since 2025-01-01
scripts/meeting_notes list --until 2025-01-31
scripts/meeting_notes list --since 2025-01-01 --until 2025-01-31

# Filter by status
scripts/meeting_notes list --status synced    # fully processed
scripts/meeting_notes list --status discovered  # pending classification

# Filter by Gemini availability
scripts/meeting_notes list --has-gemini       # with transcripts
scripts/meeting_notes list --no-gemini        # missing transcripts

# Filter by special flags
scripts/meeting_notes list --orphaned         # Gemini without calendar events
scripts/meeting_notes list --one-on-ones      # 1:1 meetings only

# Combine filters and limit results
scripts/meeting_notes list --tag rhdh --recurring --since 2025-01-01 --limit 10

# Sort options
scripts/meeting_notes list --sort title       # alphabetical
scripts/meeting_notes list --oldest           # oldest first (default: newest)
```

**Output format:**

```
Meetings
==========================================================================================
DATE         TAG             R   G   TITLE
------------------------------------------------------------------------------------------
2025-01-10   rhdh            r   ✓   RHDH Standup
2025-01-09   one-on-ones     r   ✓   1:1 with Alice
2025-01-08   team            o   -   Planning Session

Total: 3 meeting(s)
```

### Show Meeting Details

```bash
# View full details for a specific meeting
scripts/meeting_notes show <stable_id>
scripts/meeting_notes show rhdh-standup-2025-01-10
```

Shows:

- Core info (date, time, tag, status, directory)
- Flags (one-on-one, orphaned, manual capture needed)
- Gemini asset URLs (transcript, summary)
- Calendar metadata (attendees, organizer, location, attachments)

**AI Agent workflow for browsing:**

```bash
# 1. Get list as JSON
scripts/meeting_notes --json list --tag rhdh --limit 10

# 2. Parse JSON to display to user
# 3. User selects a meeting
# 4. Get details as JSON
scripts/meeting_notes --json show <stable_id>
```

### Edit Meeting Metadata

Modify tag, recurring flag, or slug for existing meetings:

```bash
# Change tag
scripts/meeting_notes edit <stable_id> --tag team

# Change recurring/one-off
scripts/meeting_notes edit <stable_id> --recurring
scripts/meeting_notes edit <stable_id> --one-off

# Change slug
scripts/meeting_notes edit <stable_id> --slug new-meeting-name

# Combine changes
scripts/meeting_notes edit <stable_id> --tag rhdh --recurring
```

**Note:** Editing updates the database only. Run `doctor --fix` to sync the filesystem.

### Doctor (Consistency Check)

Check and fix inconsistencies between the database and filesystem:

```bash
# Check for issues (dry-run)
scripts/meeting_notes doctor

# Fix issues (move files to match DB)
scripts/meeting_notes doctor --fix
```

**Detects:**

- Path mismatches (DB path ≠ actual filesystem location)
- Orphaned directories (files without DB record)

**Typical workflow after edits:**

```bash
# Edit meeting metadata
scripts/meeting_notes edit <stable_id> --tag new-tag

# Check what would change
scripts/meeting_notes doctor

# Apply filesystem changes
scripts/meeting_notes doctor --fix
```

## Tag Management

Tags categorize meetings and are stored in the JSONL database with optional metadata.

**List all tags:**

```bash
scripts/meeting_notes tags
scripts/meeting_notes --json tags  # For AI agents
```

**Create a new tag:**

```bash
scripts/meeting_notes tags add <name> [-d "description"] [-c "#hexcolor"]

# Examples:
scripts/meeting_notes tags add rhdh -d "Red Hat Developer Hub meetings" -c "#e63946"
scripts/meeting_notes tags add one-on-ones -d "1:1 meetings" -c "#457b9d"
```

**Edit tag metadata:**

```bash
scripts/meeting_notes tags edit <name> [-d "new description"] [-c "#newcolor"]
```

**Rename a tag:**

```bash
scripts/meeting_notes tags rename <old_name> <new_name>
```

Note: This renames the tag definition but does NOT update existing meetings. A migration may be needed.

**Delete a tag:**

```bash
scripts/meeting_notes tags delete <name>
scripts/meeting_notes tags delete <name> --force  # Delete even if meetings use it
```

**Tag record schema (JSONL):**

```json
{
  "type": "tag",
  "stable_id": "rhdh",
  "data": {
    "name": "rhdh",
    "description": "Red Hat Developer Hub meetings",
    "color": "#e63946",
    "created_at": "2026-01-12T...",
    "updated_at": "2026-01-12T..."
  }
}
```

**AI Agent workflow for tag management:**

1. Run `scripts/meeting_notes --json tags` to list current tags
2. Parse JSON to show user the tags with meeting counts
3. If user wants to add/edit/rename tags, use AskUserQuestion to confirm
4. Execute the appropriate `tags` subcommand

## State Management

**v2 Architecture:** The tool uses a JSONL database stored at the **repository root**:

```
<repo-root>/
  .meeting-notes/
    meetings.jsonl     # All meeting records (append-only)
    sync.jsonl         # Sync state records
    index.json         # Current state snapshot (rebuilt on startup)
  meetings/            # Output directory (filesystem structure)
```

The database stores:

- Meeting records with full metadata (title, date, attendees, Gemini assets)
- Sync state (timestamps, processed counts)
- Recurring patterns cache (for automatic classification)
- Tag definitions (name, description, color)
- Ignored patterns (meetings to skip)

**Key features:**

- **Append-only JSONL**: Each change appends a new record, enabling full audit trail
- **In-memory index**: Fast queries via snapshot, rebuilt on startup
- **Single source of truth**: All state in one place (no more fragmented state files)

**Important:** Events are only marked as "synced" after successful download. This means:

- Running `sync` multiple times is safe - it will rediscover pending meetings
- Only after `decide` + `download` complete are events marked synced
- If you interrupt the workflow, the next `sync` will show the same meetings again

## Standard Workflow

**Interactive workflow (recommended):**

```bash
# Step 1: Discover and match
scripts/meeting_notes sync
# → Review the decision table shown

# Step 2: After reviewing, apply decisions
# Option A: Accept all suggestions
scripts/meeting_notes decide --accept-all

# Option B: Override specific meetings, then accept the rest (recommended for small changes)
scripts/meeting_notes decide 7=rhdh,r 13=one-on-ones,r  # Override only #7 and #13
scripts/meeting_notes decide --accept-all               # Accept remaining suggestions

# Option C: Specify all meetings manually (for complete control)
scripts/meeting_notes decide 1=rhdh,r 2=team,o 3=one-on-ones,r ...

# Step 3: Download assets (after user approves)
scripts/meeting_notes download
```

**Note:**

- Always review the decision table before applying
- The two-step approach (Option B) is ideal when you agree with most suggestions
- The skill should ask for approval at each step

## Script Reference

**Location:** `scripts/meeting_notes` (recommended) or `scripts/meeting_notes` (legacy)

**Key commands:**

- `init` - Initialize database and configuration
- `sync` - Combined calendar discovery + Gemini email matching
- `decide` - Apply recurring and tag decisions
- `download` - Download meeting assets
- `status` - Check sync status
- `list` - Browse meetings with filters (tag, recurring, time, status)
- `show` - Display detailed info for a single meeting
- `edit` - Modify meeting metadata (tag, recurring, slug)
- `doctor` - Check/fix DB vs filesystem inconsistencies
- `tags` - Manage tag definitions (list, add, edit, rename, delete)
- `compact` - Compact JSONL database (remove obsolete records)

**Global flags:**

- `--json` - Output in JSON format (machine-readable, recommended for AI agents)
- `--verbose` - Enable verbose logging
- `--debug` - Enable debug mode

**Configuration:** `.meeting-notes.json` (automatically created with defaults)

**Database:** `.meeting-notes/` directory at repository root (JSONL files)

**Requirements:**

- `gwt` CLI tool (Google Workspace Tools) installed
- Google Workspace authentication configured (run `gwt credentials login`)
- Python 3.10+ (standard library only)

**Configuration:** The script uses `.meeting-notes.json` with these key settings:

- `gwt_command`: Full path to gwt binary (default: `/Users/mhild/src/rhdh/sidekick/google-workspace-tools/.venv/bin/gwt`)
- `user_email`: Your email address (used for 1:1 detection)

## Execution Pattern

**CRITICAL: This is an INTERACTIVE skill. Never auto-apply decisions without explicit user approval.**

When the user requests a meeting notes sync:

1. **Determine skill location:** Find where this SKILL.md is located and derive the script path from it
2. **Construct script path:** Build full path to `scripts/meeting_notes` from the skill directory
3. **Check current location:** Verify working directory is the pensieve repository root
4. **Run sync command with --json:** Execute `<skill-path>/scripts/meeting_notes sync --json`
5. **Parse JSON output:**
   - Extract `sync_summary`, `decision_table`, and `next_steps`
   - Analyze meetings for patterns (1:1s, recurring team meetings, one-offs, etc.)
   - Group similar meetings for intelligent proposals
6. **Present decision table and make intelligent proposals using AskUserQuestion:**
   - **CRITICAL:** Use the AskUserQuestion tool (not just text)
   - First, display the decision table in human-readable format (from decision_table.meetings)
   - Then analyze patterns and create grouped proposals:
     - Example: "I see 5 one-on-one meetings, 3 RHDH team meetings, and 2 planning sessions"
     - Group by pattern: "Meetings #1-5 appear to be 1:1s, suggest: one-on-ones,r"
     - Highlight exceptions: "Meeting #8 looks unusual (title doesn't match pattern)"
   - Question: "How would you like to classify these 10 meetings?"
   - Header: "Meeting Classification"
   - Options (customize based on detected patterns):
     1. label: "Accept all suggestions (Recommended)", description: "Apply suggested tags and recurring/one-off settings for all 10 meetings"
     2. label: "Accept patterns, customize anomalies", description: "Auto-classify the 8 meetings that match patterns (#1-5, #6-7), then I'll help with the 2 outliers (#8, #10)"
     3. label: "Review each meeting", description: "I'll show each meeting for individual decisions"
     4. label: "Skip for now", description: "Stop here and review later"
   - multiSelect: false
7. **Apply decisions based on user choice:**
   - If "Accept all suggestions": Run `<skill-path>/scripts/meeting_notes decide --accept-all`
   - If "Make manual changes":
     - Ask which meetings to change (get specific numbers and desired tag/recurring values)
     - Run `<skill-path>/scripts/meeting_notes decide [changes]` with only the overrides
     - Then run `<skill-path>/scripts/meeting_notes decide --accept-all` to apply suggestions to remaining meetings
     - Example: User wants to change #7 and #13 → Run `decide 7=rhdh,r 13=one-on-ones,r` then `decide --accept-all`
   - If "Skip for now": Stop and inform user they can run decide later
8. **After decide succeeds, use AskUserQuestion for download:**
   - Question: "Ready to download meeting transcripts, summaries, and attachments?"
   - Header: "Download"
   - Options:
     1. label: "Yes, download now (Recommended)", description: "Download all meeting assets to the meetings directory"
     2. label: "Skip download", description: "I'll download later manually"
   - multiSelect: false
   - If "Yes": Execute `<skill-path>/scripts/meeting_notes download`
   - If "Skip": Stop and inform user they can run download later
9. **Report summary:** Inform user of results

**Important:**

- ALWAYS use AskUserQuestion tool for approvals (never just ask in text)
- The user MUST see the decision table output before being asked to approve
- Never run `decide` or `download` automatically without approval
- `<skill-path>` should be derived from this SKILL.md file's location (e.g., if SKILL.md is at `/path/to/meeting-notes/SKILL.md`, then `<skill-path>` is `/path/to/meeting-notes`)

## Common Scenarios

### First-Time Sync

On first run, the tool syncs the last 7 days of meetings:

```bash
scripts/meeting_notes sync
scripts/meeting_notes decide --accept-all
scripts/meeting_notes download
```

### Incremental Sync

Subsequent syncs fetch only new meetings since last check:

```bash
scripts/meeting_notes sync
scripts/meeting_notes decide --accept-all
scripts/meeting_notes download
```

### Custom Date Range

Sync specific date range:

```bash
scripts/meeting_notes sync --after 2025-01-01 --before 2025-01-31
scripts/meeting_notes decide --accept-all
scripts/meeting_notes download
```

### Status Check

Check when meetings were last synced:

```bash
scripts/meeting_notes status
```

## Error Handling

**Authentication errors:**

- Check authentication status: `gwt credentials status`
- Re-authenticate if needed: `gwt credentials login`
- The script will automatically prompt for authentication if needed

**gwt command not found:**

- Update `gwt_command` in `.meeting-notes.json` to point to your gwt installation
- Find gwt location with: `which gwt`
- If missing, install from: https://github.com/taylorwilsdon/google-workspace-tools

**Permission errors:**

- Some Google Drive files may be restricted
- Failed downloads are reported at the end with URLs for manual review

**Orphaned emails:**

- Gemini emails without calendar events are marked as "orphaned"
- These represent meetings the user wasn't invited to but received notes for
- Review and decide if they should be included

## Integration Notes

This skill focuses solely on the meeting notes sync workflow. It does not:

- Create GTD issues (handle separately)
- Log to jrnl (handle separately)
- Analyze meeting content (separate skill)

For meeting content analysis and action item extraction, use the meeting notes after they've been synced.

## Best Practices

**Run regularly:** Sync at least weekly to keep up with new meetings

**Review suggestions:** The tool provides intelligent suggestions for recurring/tags, but verify accuracy

**Tag consistently:** Use consistent tags for better organization over time

**Check failures:** Review any download failures and manually access files if needed

**State file:** Don't manually edit `.meeting-notes-state.json` - let the tool manage it

## Quick Reference

```bash
# Initialize (first time)
scripts/meeting_notes init

# Complete workflow
scripts/meeting_notes sync && \
scripts/meeting_notes decide --accept-all && \
scripts/meeting_notes download

# Check what's synced
scripts/meeting_notes status

# Browse meetings
scripts/meeting_notes list                    # all meetings
scripts/meeting_notes list --tag rhdh         # filter by tag
scripts/meeting_notes list --recurring        # recurring only
scripts/meeting_notes list --since 2025-01-01 # date range
scripts/meeting_notes show <stable_id>        # meeting details

# Compact database (optional, removes obsolete records)
scripts/meeting_notes compact

# Help
scripts/meeting_notes --help
scripts/meeting_notes list --help
```

## Architecture (v2)

The refactored architecture uses a clean separation of concerns:

```
scripts/meeting_notes_lib/
  db.py                    # JSONL database core
  models.py                # Data models (Meeting, Pattern, etc.)

  repositories/
    meeting_repo.py        # Meeting data access
    pattern_repo.py        # Pattern cache data access
    sync_repo.py           # Sync state data access

  services/
    calendar_utils.py      # Shared calendar utilities
    discovery.py           # DiscoveryService (calendar + email)
    decision.py            # DecisionService (classification)
    downloads.py           # DownloadService (asset download)
    output_sync.py         # OutputSyncService (DB -> filesystem)
```

Key improvements over v1:

- **Single JSONL database** instead of fragmented state files
- **Repository pattern** for clean data access
- **Service layer** eliminates 100+ lines of duplicated code
- **Testable architecture** with dependency injection
