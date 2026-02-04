# GTD Skill Design

This document captures the architectural principles and design decisions for the GTD skill.

## Core Philosophy

**Trust through constraints.** The GTD skill deliberately limits flexibility to ensure the system stays trusted. Users get a working GTD implementation, not an extensible framework.

---

## Principle 1: Closed Label Taxonomy

**Rule: Exactly 12 labels. No exceptions.**

| Dimension | Labels | Question Answered |
|-----------|--------|-------------------|
| Context (4) | focus, meetings, async, offsite | Where/when can I do this? |
| Energy (2) | high, low | How much mental effort? |
| Status (3) | active, waiting, someday | Where in the workflow? |
| Horizon (3) | action, project, goal | What altitude? |

**Why closed?**

1. **Prevents taxonomy drift** — Open systems accumulate labels like `urgent`, `blocker`, `v2`, creating navigation chaos
2. **Forces thoughtful classification** — Users choose the closest match, not create pseudo-labels
3. **Enables reliable filtering** — CLI can confidently parse and combine labels
4. **Embeds methodology** — Each dimension maps 1:1 to GTD concepts

**What we deliberately exclude:**

- `urgent` — Use `--due-before` or `--overdue` filters instead
- `priority` — Energy + context sorting is sufficient; priorities corrupt systems
- `team` — GTD manages personal workflow, not team collaboration
- `feature`, `v1`, `v2` — Use projects/milestones for organizational concerns

---

## Principle 2: Two-Tier Tracking

**Rule: GitHub Issues for execution. Prose for reflection.**

| What | Where | Format | Why |
|------|-------|--------|-----|
| Actions (Ground) | GitHub Issues | `horizon/action` label | Trackable, closeable |
| Projects (H1) | GitHub Milestones | `horizon/project` label | Progress tracking |
| Areas (H2) | `2_Areas/` folder | PARA folders | Ongoing, never "complete" |
| Goals (H3) | GitHub Issues | `horizon/goal` label | Trackable, closeable |
| Vision (H4) | `HORIZONS.md` | Prose | Reflective, inspirational |
| Purpose (H5) | `HORIZONS.md` | Prose | Guides, not tasks |

**Why this split?**

- **Issues for execution energy** — Things you can complete, block, have deadlines
- **Prose for reflection energy** — Things that inspire and guide without being "completed"
- **Folders for balance** — Areas (H2) need balance checks, not completion tracking

---

## Principle 3: Metadata in HTML Comments

**Rule: GTD metadata lives in invisible HTML comments inside issue bodies.**

```html
<!-- gtd-metadata: {"due":"2026-01-15","waiting_for":{"person":"Alice"}} -->
```

**Why HTML comments?**

1. **Invisible to GitHub UI** — Rendered markdown never shows the comment
2. **Survives manual edits** — Users editing in GitHub UI don't corrupt metadata
3. **No external service** — GitHub Issues alone, no Projects upgrade needed
4. **Self-contained** — Metadata travels with the issue

**Metadata fields:**

- `due` — Hard deadline
- `defer_until` — Don't surface until this date
- `waiting_for` — Who you're waiting on (plain text, NO @mentions)
- `blocked_by` — List of blocking issue IDs

---

## Principle 4: Review Cadences

**Rule: Four cadences, each with explicit completion tracking.**

| Cadence | Interval | Focus | Purpose |
|---------|----------|-------|---------|
| Daily | 1 day | Ground | Tactical: what to work on today |
| Weekly | 7 days | Ground + H1 | Tactical: renegotiate commitments |
| Quarterly | 90 days | H1-H3 | Strategic: project/goal alignment |
| Yearly | 365 days | H3-H5 | Strategic: life direction |

**Auto-completion:** Running `gtd daily` automatically marks the review complete. No manual confirmation.

**Overdue surfacing:** The status output shows the most overdue review first with a prominent banner.

---

## Principle 5: Backend Abstraction

**Rule: Same GTD semantics, different storage. Backend never leaks.**

| Backend | Use Case | Storage |
|---------|----------|---------|
| GitHub | Teams, public visibility | GitHub Issues + Milestones |
| Taskwarrior | Privacy, offline work | Local `.gtd/taskwarrior/` |

**Why two backends?**

- **GitHub** — Native issue tracking, visible to collaborators
- **Taskwarrior** — No external dependencies, repo-local data

The `GTDStorage` abstract class defines the interface. Backends implement concrete methods.

**Critical: No backend leakage.**

The backend choice must be invisible to users in:

- **CLI output** — Never say "GitHub Issue #42" or "Taskwarrior task". Just "#42" or "item #42"
- **Workflows** — Review guides reference `$GTD` commands, never `gh issue` or `task`
- **Error messages** — "Item not found" not "GitHub issue not found"
- **Documentation** — SKILL.md describes GTD concepts, not GitHub/Taskwarrior features

**Test:** A user switching backends should see identical CLI output and workflow behavior. The only visible difference is configuration (`gtd init github` vs `gtd init taskwarrior`).

---

## Principle 6: Inbox = Unclarified

**Rule: An item is "inbox" if it lacks horizon, context, OR energy classification.**

```python
def is_inbox(self) -> bool:
    has_horizon = any(label.startswith("horizon/") for label in self.labels)
    has_context = any(label.startswith("context/") for label in self.labels)
    has_energy = any(label.startswith("energy/") for label in self.labels)
    return not has_horizon and not has_context and not has_energy
```

**Why this definition?**

- Forces all captured items through clarification
- Prevents tasks sitting in ambiguous states
- `gtd capture` only adds `status/someday` — item remains inbox until clarified

---

## Principle 7: CLI-Only Workflow

**Rule: All GTD operations route through the CLI.**

Users should never:

- Manually create issues in GitHub UI
- Manually edit labels in GitHub UI
- Edit metadata HTML comments directly

**Why CLI-only?**

- Ensures consistent labeling
- Preserves metadata integrity
- Enforces GTD workflow (capture → clarify → organize)

---

## Principle 8: Repo-Local Configuration

**Rule: Configuration lives in `.gtd/config.json` at repo root.**

```json
{
  "backend": "github"
}
```

**Why repo-local?**

- GTD config is per-project, not global
- Enables different workflows per repository
- No walking up parent directories (prevents stray config pickup)

---

## Principle 9: Append-Only History

**Rule: All actions log to `.gtd/history.log` in JSONL format.**

```jsonl
{"ts":"2026-01-20T08:30:00","action":"capture","item_id":"123","title":"Review PR"}
{"ts":"2026-01-20T10:00:00","action":"review","type":"daily"}
```

**Why JSONL?**

- Append-only (no file corruption risk)
- Streamable (no memory issues with large logs)
- Machine-readable for analytics

---

## Anti-Patterns (What We Avoid)

| Anti-Pattern | Why It's Bad | Our Approach |
|--------------|--------------|--------------|
| Extensible label systems | Taxonomy drift, navigation chaos | Closed 12-label taxonomy |
| Everything in issues | Vision/purpose become task backlogs | Prose for H4/H5 |
| Manual GitHub editing | Inconsistent labeling, broken metadata | CLI-only workflow |
| Global configuration | Project bleed, wrong context | Repo-local `.gtd/` |
| Priority labels | Everything becomes urgent | Energy + context filtering |
| @mention in waiting_for | Unwanted notifications | Plain text names |

---

## Extension Points

Future enhancements can add without breaking:

1. **New metadata fields** — Add to `GTDMetadata` dataclass
2. **New backends** — Implement `GTDStorage` ABC
3. **Recurring tasks** — Add `--recurring` flag to CLI
4. **GitHub Projects** — Optional integration for date fields

All extensions must preserve the closed taxonomy and core workflow.
