# README Example

**Output**: Map entry point

```markdown
# Code Map - Order Service

REST API for customer order management with inventory and payment integration.

## Domains Index

| Domain | Path | Purpose |
|--------|------|---------|
| Auth | [domains/auth.md](domains/auth.md) | User identity and access control |
| Orders | [domains/orders.md](domains/orders.md) | Order lifecycle management |
| Inventory | [domains/inventory.md](domains/inventory.md) | Stock tracking and reservations |
| Payments | [domains/payments.md](domains/payments.md) | Payment processing integration |

## Quick Navigation

- **New to the codebase?** Start with [ARCHITECTURE.md](ARCHITECTURE.md)
- **Adding a feature?** Find the relevant domain, read its L1 doc
- **Debugging?** Use grep: `grep "\[L1:orders\]" domains/`

## Navigation

Read [ARCHITECTURE.md](ARCHITECTURE.md) for system overview.
```

## Key Points

- **One paragraph description**: What is this project?
- **Domains table**: Auto-generated, review for accuracy
- **Quick Navigation**: Task-oriented hints for common use cases
- Keep it short—this is just an entry point
