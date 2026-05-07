# L2: Module Doc Example

**Input**: Python source file

```python
# src/auth/oauth.py
"""OAuth 2.0 authentication implementation.

Handles token exchange, refresh, and validation for third-party OAuth providers.
"""

from typing import Optional
from .tokens import TokenStore

class OAuthClient:
    """Client for OAuth 2.0 authorization code flow."""

    def __init__(self, provider: str, client_id: str):
        """Initialize OAuth client for a provider."""
        self.provider = provider
        self.client_id = client_id
        self._store = TokenStore()

    def authorize(self, redirect_uri: str) -> str:
        """Generate authorization URL for user redirect."""
        ...

    def exchange(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        ...

def validate_token(token: str) -> Optional[dict]:
    """Validate and decode a JWT token.

    Returns claims dict if valid, None if expired or invalid.
    """
    ...
```

**Output**: Generated module doc

```markdown
# [L2:oauth] OAuth Module

[Source](../../../src/auth/oauth.py)

OAuth 2.0 authentication implementation.

Handles token exchange, refresh, and validation for third-party OAuth providers.

## Classes

### [`OAuthClient`](../../../src/auth/oauth.py#L10)

Client for OAuth 2.0 authorization code flow.

| Method | Description |
|--------|-------------|
| [`authorize`](../../../src/auth/oauth.py#L19) | Generate authorization URL for user redirect |
| [`exchange`](../../../src/auth/oauth.py#L23) | Exchange authorization code for tokens |

## Functions

| Function | Description |
|----------|-------------|
| [`validate_token`](../../../src/auth/oauth.py#L27) | Validate and decode a JWT token |
```

## Key Points

- Module docstring becomes the description
- Classes and functions extracted with line numbers
- Method docstrings become table descriptions
- Source link at top for navigation back to code
