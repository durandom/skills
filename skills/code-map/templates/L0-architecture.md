# [L0:architecture] Project Name

<!-- SIZE LIMIT: This file must stay under 500 lines. If exceeding, split into more L1 domains. -->

## [L0:overview] System Overview

<!-- FILL: One-paragraph description of what this system does -->

**Purpose:** <!-- FILL: Primary purpose -->

**Users:** <!-- FILL: Who uses this system -->

## [L0:stack] Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
<!-- FILL: Add rows for each technology -->
| Runtime | [language] | [purpose] |
| Framework | [framework] | [purpose] |
| Storage | [database] | [purpose] |
| External | [service] | [purpose] |

## [L0:diagram] High-Level Architecture

<!-- FILL: Replace with actual architecture diagram -->

```
┌─────────────────────────────────────────────────────────────┐
│                        [System Name]                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐         │
│   │  Input    │───▶│ Processing│───▶│  Output   │         │
│   │  Layer    │    │   Layer   │    │  Layer    │         │
│   └───────────┘    └───────────┘    └───────────┘         │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          ▼                                  │
│                   ┌───────────┐                            │
│                   │  Storage  │                            │
│                   └───────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**

1. <!-- FILL: Step 1 of main data flow -->
2. <!-- FILL: Step 2 -->
3. <!-- FILL: Step 3 -->

## [L0:domains] Domain Map

<!-- FILL: List all L1 domains. Each domain gets its own file in domains/ -->

- [Domain One](domains/domain-one.md) - <!-- FILL: Brief purpose -->
- [Domain Two](domains/domain-two.md) - <!-- FILL: Brief purpose -->
- [Domain Three](domains/domain-three.md) - <!-- FILL: Brief purpose -->

## [L0:entry-points] Entry Points

### CLI Commands
<!-- FILL: List main CLI entry points with code links -->

| Command | Code Link | Description |
|---------|-----------|-------------|
| `command` | [`main`](../src/cli.py#L15) | <!-- FILL: What it does --> |

### API Endpoints
<!-- FILL: If applicable, list API entry points -->

| Endpoint | Code Link | Description |
|----------|-----------|-------------|
| `GET /api/...` | [`handler`](../src/api.py#L20) | <!-- FILL: What it does --> |

### Programmatic
<!-- FILL: Main functions/classes for library usage -->

- [`ClassName`](../src/main.py#L10) - <!-- FILL: Description -->
- [`function_name()`](../src/main.py#L50) - <!-- FILL: Description -->

## [L0:patterns] Key Patterns

<!-- FILL: Document architectural patterns used in this codebase -->

### Pattern Name
<!-- FILL: Brief description -->

**Where used:** <!-- FILL: File or domain references -->

**Example:**

```python
# FILL: Code snippet showing the pattern
```

---

<!--
FILL INSTRUCTIONS:
1. Replace "Project Name" with actual project name
2. Write system overview paragraph
3. Fill in technology stack table
4. Update architecture diagram to match actual system
5. List all L1 domains with links (create domain files first)
6. Add entry points with code links (run validation to verify)
7. Document any consistent patterns used

Keep this file under 500 lines. If you need more space, create L1 domain docs.
-->
