# L1: Domain Doc Example

**Input**: Multiple L2 module docs (oauth.md, tokens.md, sessions.md)

**Output**: Domain doc synthesizing modules

```markdown
# [L1:auth] Authentication Domain

Handles user identity, access control, and session management.

## Purpose

The auth domain ensures only authenticated users access protected resources.
It supports multiple auth methods (OAuth, API keys, sessions) with a unified interface.

## Modules

| Module | Purpose |
|--------|---------|
| [OAuth](modules/oauth.md) | Third-party OAuth 2.0 flow |
| [Tokens](modules/tokens.md) | JWT creation and validation |
| [Sessions](modules/sessions.md) | Server-side session storage |
| [Decorators](modules/decorators.md) | Route protection utilities |

## Depends On

| Domain | Reason |
|--------|--------|
| [Database](database.md) | User records, session storage |
| [Config](config.md) | OAuth credentials, token secrets |

## Data Flow

1. Request arrives with credentials (token, session, OAuth code)
2. Credentials validated, user loaded
3. User context available to handlers
4. Session/token refreshed as needed
```

## Key Points

- **Synthesize from L2**: Don't repeat module details, summarize them
- **Link to modules only**: L1 links to `modules/*.md`, never source
- **No symbols or line numbers**: Describe *what*, not *which function*
- **Purpose section**: What problem does this domain solve?
- **Dependencies**: Cross-domain relationships
- Stay under 300 lines
