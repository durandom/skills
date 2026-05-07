# GTD Skill TODO

## Work Items

### Extract taxonomy into configuration

**Goal:** Make label taxonomy configurable per-repo rather than hardcoded.

**Status:** Future work - requires configuration file support

---

### ~~Remove area and type labels~~ ✅

**Goal:** Remove project-specific labels to make the GTD skill reusable.

**Changes:**

- [x] Remove `area/*` labels (8 labels) - organization-specific
- [x] Remove `type/*` labels (4 labels) - "achievement" and "blocked" are non-standard GTD

**Keep (4 dimensions):**

- `context/*` - focus, meetings, async, offsite
- `energy/*` - high, low
- `horizon/*` - now, soon, later, waiting
- `priority/*` - urgent, high, normal, low

### ~~Project integration / PARA~~ ✅

**Status:** Answered — no code changes needed. Current design is correct.

**Questions and Answers:**

#### Q1: How do we integrate with PARA?

**Answer: We don't — and that's intentional.**

GTD and PARA serve different purposes and should remain decoupled:

| System | Purpose | Storage | Tracks |
|--------|---------|---------|--------|
| GTD | Execution workflow | GitHub Issues | Actions, Projects (H1), Goals (H3) |
| PARA | Filing system | Filesystem | Notes, docs, reference materials |

**Integration points (already in place):**

1. **Projects (H1):** GTD milestones can *correspond* to PARA `1_Projects/` folders, but they're separate. Use `para sync` to check alignment.
2. **Areas (H2):** Live exclusively in PARA's `2_Areas/` folder. GTD review workflows tell users to "glance at `2_Areas/`" — that's the integration. No GTD field needed.
3. **Resources (H3) / Archive (H4):** Pure PARA concepts, no GTD equivalent.

**Why no tighter coupling?**

- **Dependency direction:** GTD is foundational (task workflow); PARA is organizational. GTD should work without PARA configured.
- **We already removed `area/*` labels:** Re-adding area tracking would undo that deliberate decision.
- **Different lifecycles:** GTD items complete; Areas never do. Mixing them creates conceptual confusion.

#### Q2: Should every issue have a project assigned?

**Answer: No.**

Not every GTD item needs a project:

| Item Type | Needs Project? | Why |
|-----------|----------------|-----|
| `horizon/action` (standalone) | Optional | "Buy milk" doesn't need a project |
| `horizon/action` (part of outcome) | Yes | "Write intro section" → project "Launch Blog" |
| `horizon/project` | N/A | It *is* the project (milestone) |
| `horizon/goal` | No | Goals guide projects, not the reverse |

**Current behavior is correct:** The `--project` flag is optional. Forcing it would add friction to quick captures.

**When to encourage projects:** Weekly review already surfaces "stalled projects" (projects with no active actions). That's sufficient nudging.

#### Q3: Are areas also projects?

**Answer: No — they're fundamentally different.**

| Attribute | Project (H1) | Area (H2) |
|-----------|--------------|-----------|
| Completes? | Yes — has end state | No — ongoing responsibility |
| Tracked in | GTD (milestone + `horizon/project`) | PARA (`2_Areas/` folder) |
| Example | "Launch MVP" | "Engineering Management" |
| Review cadence | Weekly | Quarterly |

**The confusion:** Both can have actions associated with them. But:

- "Ship v1.0" is a **project** — it ends when shipped
- "Engineering Management" is an **area** — it never ends, you maintain it

**A single action can relate to both:**

> "Review team OKRs" might be in project "Q1 Planning" AND area "Engineering-Management"

But GTD only tracks the project relationship. The area relationship is implicit (you know which area your projects serve).

---

**Design decision:** GTD handles H0 (actions), H1 (projects), H3 (goals). PARA handles H2 (areas). They meet at the human level during reviews, not at the data level.
