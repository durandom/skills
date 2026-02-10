# Documentation Patterns

Reusable patterns for structuring information in your personal knowledge system.

<overview>
While PARA tells you **where** to put information and GTD tells you **what to do** with it, documentation patterns tell you **how to structure** the content itself for maximum usefulness.

These patterns complement the core methodologies by providing templates for common documentation needs.
</overview>

## Watch List Pattern

### Purpose

Track **external dependencies you can't control** - product releases, API updates, upstream fixes, industry changes. Unlike GTD's `@waiting` (for people/delegated tasks), Watch Lists track systems and products.

### When to Use

- Waiting for a software feature to be released
- Monitoring an upstream bug fix
- Tracking industry standards or API changes
- Following hardware release cycles
- Awaiting third-party integrations

### Structure

```markdown
## Watch List 👀

Features/changes to monitor for this [project/area]:

### [Feature Name] (Status: [Pending/In Beta/Delayed/Released])

| Item | Status | Last Updated |
|------|--------|--------------|
| **Version/Release** | [current version] | [date] |
| **Feature toggle** | ✅/❌ Available/Not available | [date] |
| **Working as expected** | ✅/❌ Yes/No | [date] |

**What happened:** [Brief history - what was promised, what actually shipped]

**What to watch:**
- [ ] [Specific thing to check #1]
- [ ] [Specific thing to check #2]
- [ ] [Specific thing to check #3]

**Sources:**
- [Source Name](URL)
- [Source Name](URL)
```

### Key Elements

| Element | Purpose | Example |
|---------|---------|---------|
| **Status table** | Quick glance at current state | Version, toggle availability, working status |
| **Last Updated** | Know how stale the info is | "Dec 2025" |
| **What happened** | Context for future-you | "Apple teased in beta but didn't ship" |
| **Checkboxes** | Specific triggers to monitor | "New hardware announcement" |
| **Sources** | Where to check for updates | Links to official blogs, forums |

### Relationship to GTD

| GTD Concept | Watch List Equivalent |
|-------------|----------------------|
| `@waiting` | External dependencies (systems, not people) |
| Weekly Review | Check and update Watch Lists |
| Someday/Maybe | Features you'd like but aren't actively tracking |

**During reviews:** Scan Watch Lists, update statuses, check sources for news.

### Example: tvOS Audio Passthrough

```markdown
## Watch List 👀

### tvOS Audio Passthrough (Status: Delayed)

| Item | Status | Last Updated |
|------|--------|--------------|
| **tvOS version** | 26.2 (Dec 12, 2025) | Current |
| **Passthrough API** | In codebase, not enabled | WWDC 2025 |
| **Settings toggle** | ❌ Not available | Dec 2025 |
| **TrueHD/DTS-X working** | ❌ No | Dec 2025 |

**What happened:** Apple teased passthrough in tvOS 26 betas,
developers found the APIs, but the feature did not ship in the
release. Speculation is Apple is saving it for new hardware.

**What to watch:**
- [ ] New Apple TV hardware announcement (expected Spring 2026)
- [ ] tvOS 26.x updates enabling passthrough toggle
- [ ] Infuse/Plex app updates adding passthrough support

**Sources:**
- [CE Critic - Missing Passthrough](https://cecritic.com/...)
- [MacRumors - 2025 Apple TV](https://www.macrumors.com/...)
```

### Best Practices

1. **Be specific** - "Check for feature X" not "watch for updates"
2. **Include dates** - Prevents stale information
3. **Link sources** - Know where to check without searching again
4. **Use checkboxes** - Clear triggers for action
5. **Review regularly** - Add to weekly/monthly review checklist

---

## Status Badges Pattern

### Purpose

Quick visual indicators for item state across documents.

### Structure

Use consistent emoji or text badges:

| Badge | Meaning |
|-------|---------|
| ✅ | Working/Complete/Available |
| ❌ | Not working/Unavailable |
| ⚠️ | Partial/Degraded/Workaround needed |
| ⏳ | Pending/In progress |
| 🔴 | Critical/Blocked |
| 🟡 | Warning/Attention needed |
| 🟢 | Good/Healthy |
| ⭐ | Recommended/Primary choice |

### Example

```markdown
| Feature | macOS | iOS | Notes |
|---------|-------|-----|-------|
| Sync | ✅ | ✅ | Full support |
| Offline | ✅ | ⚠️ | iOS limited to 100 items |
| Export | ✅ | ❌ | Not available on iOS |
```

---

## Decision Matrix Pattern

### Purpose

Document multi-factor decisions for future reference.

### Structure

```markdown
## [Decision Topic]

### Options Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Option A | Pro 1, Pro 2 | Con 1 | ⭐ Chosen |
| Option B | Pro 1 | Con 1, Con 2 | Rejected |

### Decision

**Chosen:** Option A

**Reasoning:** [Why this option won]

**Revisit if:** [Conditions that would change this decision]
```

### Example

```markdown
## Media Player Choice

| Option | TrueHD | DTS:X | UI | Price |
|--------|--------|-------|----|----|
| Apple TV 4K | ❌ | ❌ | ⭐ Best | $129 |
| Shield TV Pro | ✅ | ✅ | Good | $199 |
| Fire TV Cube | ❌ | ❌ | OK | $139 |

**Chosen:** Apple TV 4K

**Reasoning:** Best UI/ecosystem integration, streaming is primary use case,
local content workaround via Infuse is acceptable.

**Revisit if:** tvOS adds passthrough, or local 4K content becomes primary use.
```

---

## Changelog Pattern

### Purpose

Track what changed and when within a document.

### Structure

Add to bottom of documents that evolve:

```markdown
---

*Last updated: YYYY-MM-DD* | [Brief description of changes]
```

For more detailed tracking:

```markdown
## Changelog

| Date | Change |
|------|--------|
| 2025-12-22 | Added Watch List for tvOS passthrough |
| 2025-12-21 | Initial documentation |
```

---

## Integration with b4brain

| Pattern | Typical Location | Review Frequency |
|---------|------------------|------------------|
| Watch List | Areas (ongoing responsibilities) | Weekly/Monthly |
| Status Badges | Anywhere | As needed |
| Decision Matrix | Projects or Areas | When revisiting decisions |
| Changelog | Any evolving document | Each update |
