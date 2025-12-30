# [L1:domain-name] Domain Title

<!-- SIZE LIMIT: This file must stay under 300 lines. If exceeding, add L2 module docs. -->

## Purpose

<!-- FILL: What this domain handles and why it exists -->

**Boundaries:**

- **In scope:** <!-- FILL: What this domain IS responsible for -->
- **Out of scope:** <!-- FILL: What belongs to other domains -->

## Entry Points

<!-- FILL: List the main entry points with code links -->

| Entry Point | Description |
|-------------|-------------|
| [`ClassName`](../../src/module/file.py#L15) | <!-- FILL: What it does --> |
| [`function_name()`](../../src/module/file.py#L50) | <!-- FILL: What it does --> |

**Typical usage:**

```python
# FILL: Brief example showing how to use this domain
```

## Depends On

<!-- FILL: List dependencies on other domains and external services -->

### Internal Dependencies

- [Other Domain](other-domain.md) - <!-- FILL: Why this dependency exists -->

### External Dependencies

- **Library:** [name] - <!-- FILL: What it's used for -->
- **Service:** [name] - <!-- FILL: What it's used for -->

## Diagram

<!-- FILL: ASCII diagram showing internal structure -->

```
┌─────────────────────────────────────────┐
│            [Domain Name]                │
├─────────────────────────────────────────┤
│                                         │
│   ┌─────────┐      ┌─────────┐         │
│   │Component│─────▶│Component│         │
│   │   A     │      │   B     │         │
│   └─────────┘      └─────────┘         │
│        │                │               │
│        └───────┬────────┘               │
│                ▼                        │
│         ┌───────────┐                   │
│         │ Component │                   │
│         │    C      │                   │
│         └───────────┘                   │
│                                         │
└─────────────────────────────────────────┘
```

## Key Files

<!-- FILL: List the most important files in this domain -->

| File | Purpose |
|------|---------|
| `src/module/file.py` | <!-- FILL: What this file does --> |
| `src/module/other.py` | <!-- FILL: What this file does --> |

## Deep Dive

<!-- FILL: Only if L2 module docs exist -->

For complex internals, see module documentation:

- [Component A](modules/domain-name/component-a.md) - <!-- FILL: Brief purpose -->
- [Component B](modules/domain-name/component-b.md) - <!-- FILL: Brief purpose -->

---

<!--
FILL INSTRUCTIONS:
1. Replace "domain-name" in anchor with actual identifier (lowercase, hyphens)
2. Replace "Domain Title" with human-readable name
3. Define clear boundaries (in/out of scope)
4. Add entry points with accurate line numbers
5. List all dependencies (internal domains and external libs)
6. Update diagram to show actual internal structure
7. List key files in this domain
8. Add L2 links only if module docs exist

Keep this file under 300 lines. If you need more space, create L2 module docs.
-->
