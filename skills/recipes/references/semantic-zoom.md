# Recipe: Semantic Zoom — Controlling Abstraction Level

**Target Audience:** Developers working with AI on code, docs, research
**Goal:** Match the level of detail to your actual curiosity

---

## Foundational Principle

### The Core Insight

**Traditional text is frozen at the author's chosen abstraction level.**
AI makes text **elastic** — you control the resolution.

| Static Text | Elastic Text (AI) |
|-------------|-------------------|
| Fixed detail level | Adjust on demand |
| Skim or deep-dive (binary) | Continuous zoom |
| Author decides what matters | You decide |

### The One-Liner Test

> *"Is this response at the wrong altitude for what I need right now?"*

**Too high** → Zoom in: "Show me the implementation"
**Too low** → Zoom out: "Higher level please"

---

## Two Operations

### Zoom Out — Synthesize

Ask for high-level structure when you need orientation:

```
"Give me the high-level architecture"
"Summarize the main components"
"Make this much shorter"
"TLDR"
"Higher level of abstraction"
```

**Use when:** Starting exploration, lost in details, scanning for relevance

### Zoom In — Interrogate

Drill into specifics when you need precision:

```
"How does X work here?"
"Show me the implementation of Y"
"What edge cases does this handle?"
"Walk me through this step by step"
```

**Use when:** Debugging, implementing, verifying understanding

---

## Detection Signals

### Signal 1: Wall of Text

AI gives you 500 words when you needed 50.

**Response:** "Much more succinct please" or "TLDR"

### Signal 2: Lost in Details

You can't find the forest for the trees.

**Response:** "Give me the high-level architecture first"

### Signal 3: Vague Summary

AI is too abstract to be actionable.

**Response:** "Zoom into X specifically" or "Show me the code"

### Signal 4: Wrong Starting Point

AI explains from scratch when you know the basics.

**Response:** "I know Y, just explain the Z part"

### Signal 5: Document Rot

Knowledge docs have accumulated cruft over time.

**Response:** "Compress this document — remove outdated info and noise"

---

## Practical Patterns

### Pattern 1: Architecture-First Exploration

When opening an unfamiliar codebase:

1. "Give me the high-level architecture with ASCII diagrams"
2. Orient yourself to major components
3. "How does [specific area] work?"
4. Repeat: zoom in where curious, zoom out when lost

### Pattern 2: Research Paper Navigation

1. "Chapter-level summary"
2. "Zoom into the methodology section"
3. "What exactly is their measurement approach?"
4. Ask clarifying questions at each level

### Pattern 3: Refactoring via English

**Most powerful application:**

1. Ask AI to explain the code block in English
2. Zoom in/out until the English is crystal clear
3. Ask AI to align the code with the English

> If you can't explain it simply in English,
> the code probably shouldn't exist that way.

### Pattern 4: Debugging at Altitude

Instead of line-by-line debugging:

1. "Explain this code block in English at a high level"
2. Nonsense becomes obvious fast
3. Zoom in only where the explanation breaks down

### Pattern 5: Learning New Tools

**Before:**

```
Q: What's Cargo.toml?
A: [500 words about Rust's build system, workspaces,
    features, dependency resolution, target configs...]
```

**After:**

```
Q: What's Cargo.toml?
A: [wall of text]
Q: Much more succinct please
A: It's Rust's project config file - like package.json.
   Has metadata, dependencies, build settings.
```

Match detail to curiosity.

---

## Anti-Patterns

### Anti-Pattern 1: Accepting Default Verbosity

```
# BAD: Accepting whatever AI gives you
User: How does auth work?
AI: [2000 word essay]
User: [overwhelmed, skims, misses key point]

# GOOD: Steering the altitude
User: How does auth work? High-level first.
AI: [3 bullet points]
User: Zoom into the JWT validation part
```

### Anti-Pattern 2: Starting Too Low

```
# BAD: Diving into details without orientation
User: Explain line 47 of auth.py

# GOOD: Get context first
User: What does auth.py do overall?
User: Now explain line 47
```

### Anti-Pattern 3: Never Zooming Out

```
# BAD: Getting lost in the weeds
User: What's this variable?
User: What's this function?
User: What's this import?
[30 minutes later, still confused]

# GOOD: Reset altitude
User: I'm lost. Give me the 10,000 foot view.
```

### Anti-Pattern 4: Letting Documents Rot

```
# BAD: Knowledge docs grow forever
CLAUDE.md: 15,000 words, half outdated

# GOOD: Regular compression
User: Compress this doc. Remove outdated info.
      Delete mercilessly — Git is my backup.
```

---

## Decision Flowchart

```
           ┌─────────────────────┐
           │ AI response arrives │
           └──────────┬──────────┘
                      │
           ┌──────────▼──────────┐
           │ Is the detail level │
           │ matching your need? │
           └──────────┬──────────┘
                      │
      ┌───────────────┼───────────────┐
      │ TOO HIGH      │ JUST RIGHT    │ TOO LOW
      ▼               ▼               ▼
 ┌─────────┐    ┌─────────┐    ┌──────────────┐
 │ ZOOM IN │    │ Continue│    │ ZOOM OUT     │
 │         │    │         │    │              │
 │ "Show   │    │         │    │ "Higher      │
 │ me the  │    │         │    │ level" /     │
 │ impl"   │    │         │    │ "TLDR" /     │
 │         │    │         │    │ "Succinct"   │
 └─────────┘    └─────────┘    └──────────────┘
```

---

## Quick Reference

| Situation | Zoom Direction | Prompt |
|-----------|---------------|--------|
| Wall of text | OUT | "Much more succinct please" |
| Need orientation | OUT | "High-level architecture" |
| Need specifics | IN | "How does X work exactly?" |
| Debugging | OUT first | "Explain in English at high level" |
| Learning basics | OUT | "TLDR" / "Simpler please" |
| Verifying impl | IN | "Show me the code for X" |
| Doc maintenance | OUT | "Compress, remove outdated" |

### The Golden Rule

> **You control the altitude. AI follows.**
>
> Don't accept the default zoom level.
> Steer until detail matches curiosity.

---

## References

- [Semantic Zoom Pattern](https://github.com/lexler/augmented-coding-patterns/blob/main/documents/patterns/semantic-zoom.md)
- [Noise Cancellation Pattern](https://github.com/lexler/augmented-coding-patterns/blob/main/documents/patterns/noise-cancellation.md)
- [Excess Verbosity Obstacle](https://github.com/lexler/augmented-coding-patterns/blob/main/documents/obstacles/excess-verbosity.md)
