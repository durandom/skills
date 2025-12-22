# Recipe: Keyring Credential Storage for Python CLI Tools

A reusable pattern for secure credential storage using the system keyring with file-based fallback. Supports OAuth tokens, JSON credentials (like Google API), and generic API keys.

## Overview

This recipe provides:
- **Storage abstraction layer** with pluggable backends (keyring + file fallback)
- **Multi-account support** for OAuth-based services
- **Unified CLI command** (`credentials`) with actions: login, logout, status, import, list, migrate
- **Automatic fallback** to file storage when keyring is unavailable
- **Optional dependency** - works with or without keyring installed

## Architecture

```
src/your_package/
├── core/
│   └── storage.py      # Storage backends (copy this)
├── settings.py         # Pydantic settings with keyring config
└── cli/
    └── app.py          # Typer CLI with credentials command
```

## 1. Storage Module (`storage.py`)

This is the core abstraction - copy and adapt for your project:

```python
"""Credential storage backends for secure credential management."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class StoredCredentials:
    """Container for stored credential data.

    Adapt fields based on your credential type:
    - OAuth: token_data, client_id, client_secret, email
    - API Key: api_key, service_name
    - JSON credentials: credentials_data
    """
    token_data: dict[str, Any] = field(default_factory=dict)
    client_id: str | None = None
    client_secret: str | None = None
    email: str | None = None
    # Add additional fields as needed:
    # api_key: str | None = None


class CredentialStorage(ABC):
    """Abstract base class for credential storage backends."""

    @abstractmethod
    def load(self, account_id: str | None = None) -> StoredCredentials | None:
        """Load credentials for the given account or default account."""

    @abstractmethod
    def save(self, credentials: StoredCredentials) -> bool:
        """Save credentials. Returns True on success."""

    @abstractmethod
    def delete(self, account_id: str | None = None) -> bool:
        """Delete credentials for the given account."""

    @abstractmethod
    def list_accounts(self) -> list[str]:
        """List all stored account identifiers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this storage backend is available."""


class FileCredentialStorage(CredentialStorage):
    """File-based credential storage (fallback option)."""

    def __init__(self, token_path: Path, credentials_path: Path | None = None):
        self.token_path = token_path
        self.credentials_path = credentials_path

    def load(self, account_id: str | None = None) -> StoredCredentials | None:
        """Load credentials from file."""
        if not self.token_path.exists():
            return None

        try:
            with open(self.token_path) as f:
                token_data = json.load(f)

            return StoredCredentials(
                token_data=token_data,
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                email=None,  # File storage doesn't track email separately
            )
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load token file: {e}")
            return None

    def save(self, credentials: StoredCredentials) -> bool:
        """Save credentials to file."""
        try:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as f:
                json.dump(credentials.token_data, f, indent=2)
            return True
        except OSError as e:
            logger.error(f"Failed to save token file: {e}")
            return False

    def delete(self, account_id: str | None = None) -> bool:
        """Delete the token file."""
        if self.token_path.exists():
            try:
                self.token_path.unlink()
                return True
            except OSError as e:
                logger.error(f"Failed to delete token file: {e}")
                return False
        return False

    def list_accounts(self) -> list[str]:
        """File storage doesn't support multi-account."""
        return ["default"] if self.token_path.exists() else []

    def is_available(self) -> bool:
        """File storage is always available."""
        return True


class KeyringCredentialStorage(CredentialStorage):
    """Keyring-based secure credential storage."""

    DEFAULT_SERVICE_NAME = "your-app-name"  # CUSTOMIZE THIS
    DEFAULT_ACCOUNT = "_default"
    ACCOUNT_LIST_KEY = "_accounts"
    CLIENT_CREDENTIALS_KEY = "_client_credentials"

    def __init__(self, service_name: str = DEFAULT_SERVICE_NAME):
        self.service_name = service_name
        self._keyring = None

    @property
    def keyring(self):
        """Lazy import keyring module."""
        if self._keyring is None:
            import keyring
            self._keyring = keyring
        return self._keyring

    def _get_key(self, account_id: str | None) -> str:
        """Get the keyring key for an account."""
        return account_id or self.DEFAULT_ACCOUNT

    def load(self, account_id: str | None = None) -> StoredCredentials | None:
        """Load credentials from keyring."""
        key = self._get_key(account_id)

        try:
            data = self.keyring.get_password(self.service_name, key)

            # If no specific account and _default not found, try first from list
            if not data and not account_id:
                accounts = self.list_accounts()
                if accounts:
                    data = self.keyring.get_password(self.service_name, accounts[0])
                    logger.debug(f"Loaded credentials for {accounts[0]}")

            if not data:
                return None

            parsed = json.loads(data)
            return StoredCredentials(
                token_data=parsed.get("token", {}),
                client_id=parsed.get("client_id"),
                client_secret=parsed.get("client_secret"),
                email=parsed.get("email"),
            )
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to load from keyring: {e}")
            return None

    def save(self, credentials: StoredCredentials) -> bool:
        """Save credentials to keyring."""
        email = credentials.email
        key = self._get_key(email)

        data = {
            "token": credentials.token_data,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "email": email,
        }

        try:
            self.keyring.set_password(self.service_name, key, json.dumps(data))

            # Update account list if we have an email
            if email:
                self._add_to_account_list(email)

            return True
        except Exception as e:
            logger.error(f"Failed to save to keyring: {e}")
            return False

    def delete(self, account_id: str | None = None) -> bool:
        """Delete credentials from keyring."""
        key = self._get_key(account_id)

        try:
            self.keyring.delete_password(self.service_name, key)
            if account_id:
                self._remove_from_account_list(account_id)
            return True
        except Exception as e:
            logger.debug(f"Failed to delete from keyring: {e}")
            return False

    def list_accounts(self) -> list[str]:
        """List all stored account identifiers."""
        try:
            data = self.keyring.get_password(self.service_name, self.ACCOUNT_LIST_KEY)
            if not data:
                return []
            result = json.loads(data)
            return list(result) if isinstance(result, list) else []
        except Exception:
            return []

    def is_available(self) -> bool:
        """Check if keyring is functional."""
        try:
            self.keyring.get_keyring()
            return True
        except Exception:
            return False

    def _add_to_account_list(self, account_id: str) -> None:
        """Add account to the account list."""
        if not account_id:
            return
        accounts = set(self.list_accounts())
        accounts.add(account_id)
        try:
            self.keyring.set_password(
                self.service_name, self.ACCOUNT_LIST_KEY, json.dumps(list(accounts))
            )
        except Exception as e:
            logger.debug(f"Failed to update account list: {e}")

    def _remove_from_account_list(self, account_id: str) -> None:
        """Remove account from the account list."""
        if not account_id:
            return
        accounts = set(self.list_accounts())
        accounts.discard(account_id)
        try:
            self.keyring.set_password(
                self.service_name, self.ACCOUNT_LIST_KEY, json.dumps(list(accounts))
            )
        except Exception as e:
            logger.debug(f"Failed to update account list: {e}")

    # === Methods for OAuth client credentials (Google-style) ===

    def save_client_credentials(self, client_credentials: dict[str, Any]) -> bool:
        """Save OAuth client credentials (e.g., from Google .client_secret file)."""
        try:
            self.keyring.set_password(
                self.service_name,
                self.CLIENT_CREDENTIALS_KEY,
                json.dumps(client_credentials),
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save client credentials: {e}")
            return False

    def load_client_credentials(self) -> dict[str, Any] | None:
        """Load OAuth client credentials from keyring."""
        try:
            data = self.keyring.get_password(self.service_name, self.CLIENT_CREDENTIALS_KEY)
            if not data:
                return None
            result = json.loads(data)
            return dict(result) if isinstance(result, dict) else None
        except Exception as e:
            logger.warning(f"Failed to load client credentials: {e}")
            return None

    def has_client_credentials(self) -> bool:
        """Check if client credentials are stored."""
        try:
            data = self.keyring.get_password(self.service_name, self.CLIENT_CREDENTIALS_KEY)
            return data is not None
        except Exception:
            return False

    def delete_client_credentials(self) -> bool:
        """Delete client credentials from keyring."""
        try:
            self.keyring.delete_password(self.service_name, self.CLIENT_CREDENTIALS_KEY)
            return True
        except Exception:
            return False


# === API Key Storage (simpler use case) ===

class ApiKeyStorage(KeyringCredentialStorage):
    """Simplified storage for plain API keys."""

    API_KEY_KEY = "_api_key"

    def save_api_key(self, api_key: str, name: str = "default") -> bool:
        """Save a plain API key."""
        try:
            key = f"{self.API_KEY_KEY}_{name}"
            self.keyring.set_password(self.service_name, key, api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to save API key: {e}")
            return False

    def load_api_key(self, name: str = "default") -> str | None:
        """Load a plain API key."""
        try:
            key = f"{self.API_KEY_KEY}_{name}"
            return self.keyring.get_password(self.service_name, key)
        except Exception:
            return None

    def delete_api_key(self, name: str = "default") -> bool:
        """Delete an API key."""
        try:
            key = f"{self.API_KEY_KEY}_{name}"
            self.keyring.delete_password(self.service_name, key)
            return True
        except Exception:
            return False


# === Factory Function ===

def get_credential_storage(
    use_keyring: bool = True,
    fallback_to_file: bool = True,
    service_name: str = KeyringCredentialStorage.DEFAULT_SERVICE_NAME,
    token_path: Path | None = None,
    credentials_path: Path | None = None,
) -> CredentialStorage:
    """Factory function to get appropriate credential storage backend.

    Args:
        use_keyring: Whether to attempt using keyring
        fallback_to_file: Whether to fall back to file storage if keyring unavailable
        service_name: Service name for keyring
        token_path: Path for file-based token storage
        credentials_path: Path to client credentials file

    Returns:
        Appropriate CredentialStorage implementation

    Raises:
        RuntimeError: If keyring is required but unavailable and fallback is disabled
    """
    if use_keyring:
        try:
            storage = KeyringCredentialStorage(service_name)
            if storage.is_available():
                logger.debug("Using keyring for credential storage")
                return storage
            logger.debug("Keyring not available")
        except ImportError:
            logger.debug("Keyring module not installed")
        except Exception as e:
            logger.debug(f"Keyring unavailable: {e}")

        if not fallback_to_file:
            raise RuntimeError("Keyring unavailable and fallback to file storage disabled")

    if token_path is None:
        token_path = Path("tmp/token.json")

    logger.debug(f"Using file-based credential storage at {token_path}")
    return FileCredentialStorage(token_path, credentials_path)
```

## 2. Settings Module (`settings.py`)

Add keyring configuration to your pydantic-settings:

```python
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="MYAPP_",  # CUSTOMIZE THIS
    )

    # Credential file paths (fallback)
    credentials_path: Path = Field(
        default=Path(".credentials.json"),
        description="Path to credentials file",
    )
    token_path: Path = Field(
        default=Path("tmp/token.json"),
        description="Path to cached token",
    )

    # Keyring settings
    use_keyring: bool = Field(
        default=True,
        description="Use keyring for credential storage if available",
    )
    keyring_service_name: str = Field(
        default="my-app-name",  # CUSTOMIZE THIS
        description="Service name used for keyring storage",
    )

# Global instance
settings = Settings()
```

**Environment variables:**
- `MYAPP_USE_KEYRING=false` - disable keyring
- `MYAPP_KEYRING_SERVICE_NAME=custom-name` - change service name

## 3. CLI Commands (`cli/app.py`)

### Option A: OAuth Credentials (Google-style)

```python
import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ..core.storage import (
    FileCredentialStorage,
    KeyringCredentialStorage,
    get_credential_storage,
)
from ..settings import settings

console = Console()
app = typer.Typer()


@app.command()
def credentials(
    action: Annotated[
        str,
        typer.Argument(help="Action: login, logout, status, import, list, migrate"),
    ],
    account: Annotated[
        str | None,
        typer.Option("--account", "-a", help="Account identifier (for logout)"),
    ] = None,
    use_keyring: Annotated[
        bool,
        typer.Option("--keyring/--no-keyring", help="Use keyring storage"),
    ] = True,
    token_path: Annotated[
        Path,
        typer.Option("--token", "-t", help="Path to token file"),
    ] = Path("tmp/token.json"),
    credentials_file: Annotated[
        Path,
        typer.Option("--credentials", "-c", help="Path to credentials file"),
    ] = Path(".credentials.json"),
) -> None:
    """Manage credentials.

    Actions:
        login   - Authenticate (opens browser for OAuth)
        logout  - Remove stored credentials
        status  - Show current authentication status
        import  - Import credentials file into keyring
        list    - List all stored accounts
        migrate - Migrate file tokens to keyring
    """
    if action == "login":
        _handle_login(use_keyring, credentials_file, token_path)

    elif action == "logout":
        storage = get_credential_storage(
            use_keyring=use_keyring,
            fallback_to_file=True,
            token_path=token_path,
        )
        if storage.delete(account):
            console.print(f"[green]Logged out {account or 'default account'}[/green]")
        else:
            console.print(f"[yellow]No credentials found for {account or 'default'}[/yellow]")

    elif action == "list":
        _handle_list(use_keyring, token_path)

    elif action == "migrate":
        _handle_migrate(token_path)

    elif action == "import":
        _handle_import(credentials_file)

    elif action == "status":
        _handle_status(use_keyring, token_path, credentials_file)

    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("[dim]Valid actions: login, logout, status, import, list, migrate[/dim]")
        raise typer.Exit(1)


def _handle_login(use_keyring: bool, credentials_file: Path, token_path: Path):
    """Handle login action - implement your OAuth flow here."""
    storage_type = "keyring" if use_keyring else "file"
    console.print("[bold]Starting authentication...[/bold]")
    console.print(f"[dim]Storage: {storage_type}[/dim]")

    # TODO: Implement your OAuth flow
    # Example for Google OAuth:
    # from google_auth_oauthlib.flow import InstalledAppFlow
    # flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    # creds = flow.run_local_server(port=0)
    # ... save creds to storage

    console.print("[green]Authentication successful![/green]")


def _handle_list(use_keyring: bool, token_path: Path):
    """List credentials from all storage backends."""
    table = Table(title="Stored Accounts")
    table.add_column("Account", style="cyan")
    table.add_column("Storage", style="green")

    found_any = False

    # Check file storage
    file_storage = FileCredentialStorage(token_path)
    if file_storage.is_available():
        for acc in file_storage.list_accounts():
            table.add_row(acc, "file")
            found_any = True

    # Check keyring storage
    if use_keyring:
        try:
            keyring_storage = KeyringCredentialStorage()
            if keyring_storage.is_available():
                for acc in keyring_storage.list_accounts():
                    table.add_row(acc, "keyring")
                    found_any = True
        except ImportError:
            console.print("[dim]Keyring not installed (pip install keyring)[/dim]")

    if found_any:
        console.print(table)
    else:
        console.print("[yellow]No stored accounts[/yellow]")


def _handle_migrate(token_path: Path):
    """Migrate from file to keyring."""
    file_storage = FileCredentialStorage(token_path)
    stored = file_storage.load()

    if not stored:
        console.print("[yellow]No file-based credentials to migrate[/yellow]")
        raise typer.Exit(0)

    try:
        keyring_storage = KeyringCredentialStorage()
        if not keyring_storage.is_available():
            console.print("[red]Keyring is not available[/red]")
            raise typer.Exit(1)

        if keyring_storage.save(stored):
            console.print("[green]Successfully migrated to keyring[/green]")

            if typer.confirm("Remove file-based token?"):
                file_storage.delete()
                console.print("[dim]Removed old token file[/dim]")
        else:
            console.print("[red]Failed to save to keyring[/red]")
            raise typer.Exit(1)

    except ImportError:
        console.print("[red]Keyring not installed. Run: pip install keyring[/red]")
        raise typer.Exit(1)


def _handle_import(credentials_file: Path):
    """Import credentials file into keyring."""
    if not credentials_file.exists():
        console.print(f"[red]Credentials file not found: {credentials_file}[/red]")
        raise typer.Exit(1)

    try:
        with open(credentials_file) as f:
            creds_data = json.load(f)

        keyring_storage = KeyringCredentialStorage()
        if not keyring_storage.is_available():
            console.print("[red]Keyring is not available[/red]")
            raise typer.Exit(1)

        if keyring_storage.save_client_credentials(creds_data):
            console.print("[green]Successfully imported credentials to keyring[/green]")
            console.print("[dim]You can now delete the credentials file[/dim]")
        else:
            console.print("[red]Failed to save credentials[/red]")
            raise typer.Exit(1)

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)


def _handle_status(use_keyring: bool, token_path: Path, credentials_file: Path):
    """Show authentication status."""
    console.print("[bold]Credential Status[/bold]\n")

    # Keyring status
    if use_keyring:
        try:
            keyring_storage = KeyringCredentialStorage()
            if keyring_storage.is_available():
                console.print("  Keyring: [green]available[/green]")

                if keyring_storage.has_client_credentials():
                    console.print("  Client Credentials: [green]stored[/green]")
                else:
                    console.print("  Client Credentials: [yellow]not in keyring[/yellow]")

                accounts = keyring_storage.list_accounts()
                if accounts:
                    console.print(f"  Tokens: [green]{len(accounts)} account(s)[/green]")
                else:
                    console.print("  Tokens: [yellow]none[/yellow]")
            else:
                console.print("  Keyring: [yellow]not available[/yellow]")
        except ImportError:
            console.print("  Keyring: [dim]not installed[/dim]")

    # File storage status
    if token_path.exists():
        console.print(f"  Token File: [green]exists[/green] ({token_path})")
    else:
        console.print("  Token File: [dim]not found[/dim]")

    if credentials_file.exists():
        console.print(f"  Credentials File: [green]exists[/green] ({credentials_file})")
    else:
        console.print("  Credentials File: [dim]not found[/dim]")
```

### Option B: Simple API Key

```python
@app.command()
def api_key(
    action: Annotated[str, typer.Argument(help="Action: set, get, delete, status")],
    key_name: Annotated[str, typer.Option("--name", "-n", help="Key name")] = "default",
    value: Annotated[str | None, typer.Option("--value", "-v", help="API key value")] = None,
) -> None:
    """Manage API keys.

    Examples:
        myapp api-key set -v sk-xxx123
        myapp api-key get
        myapp api-key delete
    """
    from ..core.storage import ApiKeyStorage

    storage = ApiKeyStorage()

    if not storage.is_available():
        console.print("[red]Keyring not available[/red]")
        raise typer.Exit(1)

    if action == "set":
        if not value:
            value = typer.prompt("Enter API key", hide_input=True)
        if storage.save_api_key(value, key_name):
            console.print(f"[green]API key '{key_name}' saved[/green]")
        else:
            console.print("[red]Failed to save API key[/red]")
            raise typer.Exit(1)

    elif action == "get":
        api_key = storage.load_api_key(key_name)
        if api_key:
            console.print(f"[cyan]{api_key[:8]}...{api_key[-4:]}[/cyan]")
        else:
            console.print(f"[yellow]No API key found for '{key_name}'[/yellow]")

    elif action == "delete":
        if storage.delete_api_key(key_name):
            console.print(f"[green]API key '{key_name}' deleted[/green]")
        else:
            console.print(f"[yellow]No API key found for '{key_name}'[/yellow]")

    elif action == "status":
        api_key = storage.load_api_key(key_name)
        if api_key:
            console.print(f"  API Key '{key_name}': [green]configured[/green]")
        else:
            console.print(f"  API Key '{key_name}': [yellow]not set[/yellow]")
```

## 4. pyproject.toml

Add keyring as an optional dependency:

```toml
[project.optional-dependencies]
keyring = [
    "keyring>=25.0.0",
]

# Or include in a broader "all" extra
all = [
    "keyring>=25.0.0",
    # ... other optional deps
]
```

**Install with:**
```bash
pip install my-package[keyring]
# or
uv add my-package[keyring]
```

## 5. Testing (`tests/unit/test_storage.py`)

```python
"""Tests for credential storage backends."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from your_package.core.storage import (
    FileCredentialStorage,
    KeyringCredentialStorage,
    StoredCredentials,
    get_credential_storage,
)


class TestStoredCredentials:
    def test_creation_with_defaults(self):
        creds = StoredCredentials()
        assert creds.token_data == {}
        assert creds.client_id is None

    def test_creation_with_values(self):
        creds = StoredCredentials(
            token_data={"refresh_token": "test"},
            email="test@example.com",
        )
        assert creds.token_data["refresh_token"] == "test"
        assert creds.email == "test@example.com"


class TestFileCredentialStorage:
    def test_save_and_load(self, tmp_path: Path):
        token_path = tmp_path / "token.json"
        storage = FileCredentialStorage(token_path)

        creds = StoredCredentials(token_data={"refresh_token": "abc123"})
        assert storage.save(creds)
        assert token_path.exists()

        loaded = storage.load()
        assert loaded is not None
        assert loaded.token_data["refresh_token"] == "abc123"

    def test_load_nonexistent(self, tmp_path: Path):
        storage = FileCredentialStorage(tmp_path / "missing.json")
        assert storage.load() is None

    def test_delete(self, tmp_path: Path):
        token_path = tmp_path / "token.json"
        token_path.write_text("{}")
        storage = FileCredentialStorage(token_path)
        assert storage.delete()
        assert not token_path.exists()

    def test_is_available(self, tmp_path: Path):
        storage = FileCredentialStorage(tmp_path / "token.json")
        assert storage.is_available()


class TestKeyringCredentialStorage:
    @patch("your_package.core.storage.KeyringCredentialStorage.keyring")
    def test_save_and_load(self, mock_keyring):
        storage = KeyringCredentialStorage()

        creds = StoredCredentials(
            token_data={"refresh_token": "xyz"},
            email="test@example.com",
        )

        storage.save(creds)
        mock_keyring.set_password.assert_called()

        # Setup mock for load
        stored_data = {"token": {"refresh_token": "xyz"}, "email": "test@example.com"}
        mock_keyring.get_password.return_value = json.dumps(stored_data)

        loaded = storage.load("test@example.com")
        assert loaded is not None
        assert loaded.token_data["refresh_token"] == "xyz"

    @patch("your_package.core.storage.KeyringCredentialStorage.keyring")
    def test_is_available_success(self, mock_keyring):
        mock_keyring.get_keyring.return_value = MagicMock()
        storage = KeyringCredentialStorage()
        assert storage.is_available()

    @patch("your_package.core.storage.KeyringCredentialStorage.keyring")
    def test_is_available_failure(self, mock_keyring):
        mock_keyring.get_keyring.side_effect = Exception("No keyring")
        storage = KeyringCredentialStorage()
        assert not storage.is_available()


class TestGetCredentialStorage:
    def test_file_storage_when_keyring_disabled(self, tmp_path: Path):
        storage = get_credential_storage(
            use_keyring=False,
            token_path=tmp_path / "token.json",
        )
        assert isinstance(storage, FileCredentialStorage)

    def test_fallback_when_keyring_unavailable(self, tmp_path: Path):
        with patch(
            "your_package.core.storage.KeyringCredentialStorage.is_available",
            return_value=False,
        ):
            storage = get_credential_storage(
                use_keyring=True,
                fallback_to_file=True,
                token_path=tmp_path / "token.json",
            )
            assert isinstance(storage, FileCredentialStorage)

    def test_raises_when_keyring_required_but_unavailable(self):
        with (
            patch(
                "your_package.core.storage.KeyringCredentialStorage.is_available",
                return_value=False,
            ),
            pytest.raises(RuntimeError, match="Keyring unavailable"),
        ):
            get_credential_storage(use_keyring=True, fallback_to_file=False)
```

## Usage Examples

### OAuth Flow (Google-style)

```bash
# First time setup - import credentials file to keyring
myapp credentials import -c .client_secret.json

# Or just login (will use file if keyring import not done)
myapp credentials login

# Check status
myapp credentials status

# List accounts
myapp credentials list

# Migrate existing file token to keyring
myapp credentials migrate

# Logout specific account
myapp credentials logout -a user@example.com
```

### Simple API Key

```bash
# Set API key (will prompt for value)
myapp api-key set

# Set with specific name
myapp api-key set -n openai -v sk-xxx

# Get key
myapp api-key get -n openai

# Delete
myapp api-key delete -n openai
```

## Customization Points

1. **Service name**: Change `DEFAULT_SERVICE_NAME` in `KeyringCredentialStorage`
2. **Stored fields**: Modify `StoredCredentials` dataclass for your needs
3. **Default paths**: Adjust `token_path` defaults in settings/CLI
4. **Environment prefix**: Change `env_prefix` in pydantic settings

## Security Notes

- Keyring uses OS-native credential storage (macOS Keychain, Windows Credential Locker, Linux Secret Service)
- File fallback stores credentials in plain JSON - use only for development
- Never commit credential files to version control
- Consider adding `.token.json` and `.credentials.json` to `.gitignore`
