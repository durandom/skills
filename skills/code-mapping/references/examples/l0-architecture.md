# L0: Architecture Doc Example

**Input**: Multiple L1 domain docs

**Output**: System architecture overview

```markdown
# [L0:architecture] System Architecture

## System Overview

A REST API service for managing customer orders. Handles authentication,
order processing, inventory checks, and payment integration.

## Domains

| Domain | Purpose |
|--------|---------|
| [Auth](domains/auth.md) | User identity and access control |
| [Orders](domains/orders.md) | Order lifecycle management |
| [Inventory](domains/inventory.md) | Stock tracking and reservations |
| [Payments](domains/payments.md) | Payment processing integration |

## Data Flow

```

┌─────────┐     ┌──────┐     ┌────────┐     ┌──────────┐
│ Request │────▶│ Auth │────▶│ Orders │────▶│ Response │
└─────────┘     └──────┘     └────────┘     └──────────┘
                               │    │
                    ┌──────────┘    └──────────┐
                    ▼                          ▼
              ┌───────────┐              ┌──────────┐
              │ Inventory │              │ Payments │
              └───────────┘              └──────────┘

```

## Cross-Cutting Concerns

| Concern | Domain |
|---------|--------|
| Logging | [Observability](domains/observability.md) |
| Error handling | [Errors](domains/errors.md) |
| Configuration | [Config](domains/config.md) |
```

## Key Points

- **Synthesize from L1**: Don't repeat domain details, summarize them
- **Link to domains only**: L0 links to `domains/*.md`, never source
- **No symbols or line numbers**: Describe *what*, not *which function*
- **System Overview**: One paragraph, what does this system do?
- **Data Flow**: How do domains interact? ASCII diagrams work well
- Stay under 500 lines
