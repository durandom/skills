# Quickstart: Layton (Personal AI Assistant)

**Branch**: `001-pai-orchestrator` | **Date**: 2026-01-13

## Who is Layton?

Layton is named after [Elizabeth Layton](https://en.wikipedia.org/wiki/Elizabeth_Nel) (1917-2007), Winston Churchill's personal secretary during World War II. She was known for:

- **Anticipating needs** — entering the room ready for what was required
- **Calm efficiency** — handling the Prime Minister's demanding schedule
- **Tracking everything** — always ready with her notepad
- **Discretion** — knowing when to surface information and when to stay quiet

This skill embodies those qualities: it coordinates your other skills to manage information flow, anticipate what you need, and stay out of the way until needed.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│       SKILL.md (Probabilistic - AI Judgment)                    │
│  • Interprets your intent ("What should I work on?")            │
│  • Synthesizes information from multiple skills                 │
│  • Applies Elizabeth Layton's persona voice                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               CLI (Deterministic - Data Operations)             │
│  • gather: Query available skills                               │
│  • context: Get temporal context                                │
│  • note: Route capture to appropriate skill                     │
│  • config: Manage preferences                                   │
│  • doctor: Health check                                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Beads (State Management)                      │
│  • Focus, context, history stored as beads                      │
│  • Git-backed, designed for AI agents                           │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.11+
- Claude Code CLI environment
- (Optional) Other skills: GTD, PARA, meeting-notes

### Beads Installation (Required for State Management)

Layton uses [Beads](https://github.com/steveyegge/beads) for git-backed state management. Install the `bd` CLI:

```bash
# Install Beads CLI
pip install beads-cli

# Or with uv
uv tool install beads-cli

# Verify installation
bd --version
```

**Without Beads**: Layton's core CLI commands (`gather`, `context`, `note`, `config`) work without Beads, but you lose:

- Attention References ("Track JIRA-1234 for me")
- Focus/context state persistence across sessions
- Audit trail of interactions

Run `layton doctor` to check Beads availability—it will show a warning if `bd` CLI is not found.

## Installation

```bash
# From repository root
cd skills/layton

# The skill is ready to use - no separate installation
```

## First Run

```bash
# Check system status
./scripts/layton doctor

# Initialize personal configuration (optional)
./scripts/layton config init

# The skill works with Claude Code - invoke via SKILL.md
```

## CLI Commands (Deterministic Only)

The CLI handles data operations. AI synthesis happens in SKILL.md workflows.

### Gather Data from Skills

```bash
# Discover and query all available skills
./scripts/layton --json gather

# Query specific skills
./scripts/layton --json gather --skills gtd,para
```

### Get Temporal Context

```bash
# What time is it? Work hours?
./scripts/layton --json context
```

### Quick Capture

```bash
# Route a note to appropriate capture skill
./scripts/layton note "call dentist tomorrow"
./scripts/layton note "follow up with Sarah about API design"
```

### Configuration

```bash
# View current config
./scripts/layton config show

# Set personality option
./scripts/layton config set personality.verbosity terse

# Initialize default config
./scripts/layton config init
```

### Health Check

```bash
# Check all systems
./scripts/layton doctor

# Auto-fix issues (shown in next_steps if fixable)
./scripts/layton doctor --fix
```

## SKILL.md Workflows (Probabilistic)

These are triggered by Claude interpreting your intent:

| What You Say | Workflow |
|--------------|----------|
| "What should I know right now?" | Morning briefing |
| "What should I work on?" | Focus suggestion |
| "What's happening with Project X?" | Cross-system query |
| "Note: call dentist" | Routes to `layton note` CLI |
| "Let's do a daily/weekly review" | Periodic review |

## Skill Integration

Layton auto-detects available skills at runtime:

| Skill | What It Adds |
|-------|--------------|
| GTD | Task lists, inbox status, project tracking |
| PARA | Areas, projects, resources, archives |
| Calendar (MCP) | Events, meeting prep, time blocks |
| Meeting-Notes | Recent meeting context, action items |

**No skills required**: Layton works standalone. Each skill integration adds capability without breaking existing functionality.

## Configuration

Personal preferences are stored in `.layton/config.json`:

```json
{
  "work_schedule": { "start": "09:00", "end": "17:00" },
  "timezone": "America/Los_Angeles",
  "personality": {
    "verbosity": "terse",
    "tone": "professional"
  },
  "interaction": {
    "proactive_clarification": true,
    "teaching_mode": false
  }
}
```

## State Management

State is managed by [Beads](https://github.com/steveyegge/beads), not custom JSON files:

- Current focus → Bead with "focus" tag
- In-progress task → Linked bead
- Interaction history → Bead audit trail

## Directory Structure

```
skills/layton/
├── SKILL.md              # AI workflows and persona
├── references/
│   └── persona.md        # Elizabeth Layton background
├── workflows/
│   ├── morning-briefing.md
│   ├── focus-suggestion.md
│   └── periodic-review.md
└── scripts/
    └── layton            # Deterministic CLI

.layton/                  # Repo-local
└── config.json           # Personal configuration only

.beads/                   # State management
└── (managed by Beads)
```

## Troubleshooting

### `layton doctor` shows "Beads CLI not found"

Install the Beads CLI (see Prerequisites above):

```bash
pip install beads-cli
# or
uv tool install beads-cli
```

Layton works without Beads for basic operations, but Attention References and state persistence require it.

### "No skills detected"

This is normal if you haven't installed other skills. Layton runs in "notepad mode" standalone:

```bash
# Check what's available
./scripts/layton doctor

# Still works - just no external data
./scripts/layton context
./scripts/layton note "My first note"  # Saves to .layton/notes.jsonl
```

### Config file issues

If `doctor` reports config issues, auto-fix them:

```bash
./scripts/layton doctor --fix
```

This creates missing files with sensible defaults.

## Next Steps

1. Run `layton doctor` to verify setup
2. Configure preferences: `layton config init`
3. Start using via Claude Code with natural language
