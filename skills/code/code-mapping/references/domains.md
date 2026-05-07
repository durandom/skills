# Domains: What L1 Documentation Should Capture

Domains are semantic boundaries, not structural ones.

| What Domains ARE | What Domains are NOT |
|------------------|----------------------|
| Areas of business/functional concern | Directory names |
| Bounded contexts with clear responsibility | File groupings |
| Cohesive clusters of related concepts | Package hierarchies |
| Human-defined meaningful boundaries | Auto-detectable from code structure |

A `utils/` directory is not a domain—it's a grab-bag. A `models/` folder might contain entities from 5 different business domains. True domains might span multiple directories or cut across package structure.

## Required Sections

### 1. Purpose

> What business capability or functional area does this domain address?

Not "what the code does" but "why it exists."

**Good**: "Handles user authentication, authorization, and session management"
**Bad**: "Contains auth-related classes and functions"

### 2. Core Concepts

The key entities, value objects, and abstractions. The nouns that matter.

```markdown
## Core Concepts

- **User**: Authenticated identity with credentials
- **Session**: Time-bounded access token
- **Permission**: Named capability a user may have
```

### 3. Operations

What can you *do* in this domain? The verbs.

```markdown
## Operations

- **Authenticate**: Verify credentials, create session
- **Authorize**: Check if user has permission
- **Revoke**: Invalidate session or permission
```

### 4. Boundaries

What is explicitly NOT part of this domain? Prevents scope creep.

```markdown
## Not In This Domain

- User profile data (→ profiles domain)
- Password reset emails (→ notifications domain)
- Audit logging (→ observability domain)
```

## Optional Sections

### 5. Cross-Domain Dependencies

What other domains does this depend on? What depends on it?

```markdown
## Dependencies

**Depends On:**
- storage: for persisting sessions

**Depended On By:**
- api: for request authentication
- admin: for authorization checks
```

### 6. Entry Points

How do external callers interact with this domain?

```markdown
## Entry Points

| Entry | Purpose |
|-------|---------|
| `authenticate(credentials)` | Primary login flow |
| `AuthMiddleware` | Request-level auth check |
```

## Why Domains Require Human Judgment

The generator extracts L2 (modules) automatically—these map directly to source files.

Domains require human decisions:

1. **Semantic clustering**: What *belongs together* conceptually?
2. **Naming**: What name captures the essence?
3. **Boundaries**: Where does one domain end and another begin?
4. **Purpose**: What problem does this solve for the business?

Code structure (directories, imports) provides *hints*, but the mapping is fundamentally a human decision.

## Domain Identification Heuristics

When identifying domains in a codebase, ask:

1. **What problems does this system solve?** Each problem area may be a domain.
2. **What would you explain separately?** Concepts that need separate explanations often belong in separate domains.
3. **What could change independently?** Components with different rates of change are often different domains.
4. **What teams would own this?** Organizational boundaries often align with domain boundaries.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Domain per directory | Structure ≠ semantics |
| Domain per file type (models, views, controllers) | Cuts across business concepts |
| One giant domain | Too broad to be useful |
| Domain per class | Too granular, misses relationships |
