"""
GWT Invoker - Subprocess wrapper for Google Workspace Tools CLI.

Handles authentication and all API calls to Google Workspace services
(Calendar, Gmail, Drive) via the gwt command-line tool.
"""

import base64
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any

from .models import GWTConfig

logger = logging.getLogger(__name__)


class GWTInvoker:
    """Subprocess wrapper for gwt CLI tool."""

    def __init__(self, config: GWTConfig):
        self.config = config

    def check_authentication(self) -> bool:
        """Check if gwt is authenticated using gwt credentials status.

        Returns:
            True if authenticated, False otherwise
        """
        try:
            args = ["credentials", "status"]
            result = self._run_gwt(args, timeout=30, use_json=False)

            if result.returncode == 0:
                logger.debug("GWT authentication verified")
                return True

            logger.debug("GWT credentials status check failed")
            return False
        except Exception as e:
            logger.debug(f"Authentication check failed: {e}")
            return False

    def authenticate(self) -> bool:
        """Run gwt authentication flow interactively using gwt credentials login.

        Returns:
            True if authentication succeeded, False otherwise
        """
        logger.info("GWT authentication required")
        logger.info("Opening browser for Google authentication...")

        try:
            args = ["credentials", "login"]
            result = self._run_gwt(args, timeout=300, use_json=False, interactive=True)

            if result.returncode == 0:
                logger.info("Authentication successful")
                return True
            else:
                logger.error("Authentication failed")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Authentication timed out")
            return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def ensure_authenticated(self) -> None:
        """Ensure gwt is authenticated, running auth flow if needed.

        Raises:
            RuntimeError: If authentication fails
        """
        if not self.check_authentication():
            logger.warning("Not authenticated with Google Workspace")

            if not self.authenticate():
                raise RuntimeError(
                    "Failed to authenticate with Google Workspace. "
                    "Please ensure you have valid credentials and try again."
                )

    def _run_gwt(
        self,
        args: list[str],
        timeout: int = 60,
        use_json: bool = False,
        interactive: bool = False,
    ) -> subprocess.CompletedProcess:
        """Run gwt command and return result.

        Args:
            args: Command arguments (after 'gwt')
            timeout: Timeout in seconds
            use_json: If True, adds --json flag before the subcommand
            interactive: If True, don't capture output (for interactive commands)
        """
        # Build command with global flags first
        cmd = [self.config.gwt_command]
        if self.config.debug:
            cmd.append("-v")  # gwt uses -v for verbose/debug output
        if use_json:
            cmd.append("--json")
        cmd.extend(args)

        logger.debug(f"Running GWT command: {' '.join(cmd)}")

        try:
            if interactive:
                result = subprocess.run(
                    cmd,
                    cwd=self.config.gwt_path,
                    check=True,
                    timeout=timeout,
                )
            else:
                result = subprocess.run(
                    cmd,
                    cwd=self.config.gwt_path,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

            logger.debug("GWT command succeeded")
            if hasattr(result, "stdout") and result.stdout:
                logger.debug(f"GWT stdout:\n{result.stdout}")
            if hasattr(result, "stderr") and result.stderr:
                logger.debug(f"GWT stderr:\n{result.stderr}")

            return result

        except subprocess.CalledProcessError as e:
            logger.debug(f"gwt command failed: {' '.join(args)}")
            logger.debug(f"Exit code: {e.returncode}")
            logger.debug(f"Error output: {e.stderr}")

            # Try to extract human-friendly error from stderr
            if e.stderr:
                for line in e.stderr.split("\n"):
                    if "ERROR" in line and "|" in line:
                        parts = line.split(" - ", 1)
                        if len(parts) == 2:
                            e.gwt_error_message = parts[1].strip()
                            break
            raise

        except subprocess.TimeoutExpired:
            logger.debug(f"gwt timeout ({timeout}s): {' '.join(args)}")
            raise

    def get_calendar_events(
        self,
        time_min: str,
        time_max: str,
        calendar_id: str = "primary",
    ) -> list[dict[str, Any]]:
        """Fetch calendar events using gwt calendar command.

        Args:
            time_min: Start date (YYYY-MM-DD or ISO format)
            time_max: End date (YYYY-MM-DD or ISO format)
            calendar_id: Calendar ID (default: "primary")

        Returns:
            List of event dictionaries from the Calendar API
        """
        output_dir = self.config.gwt_output_dir / "calendar"
        output_dir.mkdir(parents=True, exist_ok=True)

        args = [
            "calendar",
            "export",
            "--calendar",
            calendar_id,
            "--after",
            time_min[:10],
            "--before",
            time_max[:10],
            "--format",
            "json",
            "--max",
            "250",
            "--output",
            str(output_dir),
        ]

        result = self._run_gwt(args, timeout=120, use_json=True)

        try:
            output_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GWT JSON output: {e}")
            return []

        if not output_data.get("success", False):
            logger.warning("GWT command reported failure")
            for error in output_data.get("errors", []):
                logger.error(f"  {error}")
            return []

        total_exported = output_data.get("total_exported", 0)
        logger.debug(f"Found {total_exported} calendar events")

        events = []
        for event_info in output_data.get("events", []):
            export_path = event_info.get("export_path")
            if export_path:
                try:
                    with open(export_path) as f:
                        event = json.load(f)
                        events.append(event)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse {export_path}: {e}")
                except Exception as e:
                    logger.warning(f"Error reading {export_path}: {e}")

        return events

    def search_gmail(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search Gmail using gwt mail command.

        Args:
            query: Gmail search query
            max_results: Maximum number of results

        Returns:
            List of messages with extracted doc links
        """
        output_dir = self.config.gwt_output_dir / "mail"
        output_dir.mkdir(parents=True, exist_ok=True)

        args = [
            "mail",
            "--query",
            query,
            "--format",
            "md",
            "--max",
            str(max_results),
            "--mode",
            "individual",
            "--output",
            str(output_dir),
        ]

        result = self._run_gwt(args, timeout=120, use_json=True)

        try:
            output_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GWT JSON output: {e}")
            return []

        if not output_data.get("success", False):
            logger.warning("GWT command reported failure")
            for error in output_data.get("errors", []):
                logger.error(f"  {error}")
            return []

        total_exported = output_data.get("total_exported", 0)
        logger.debug(f"Found {total_exported} email messages")

        messages = []
        for thread_info in output_data.get("threads", []):
            export_path = thread_info.get("export_path")
            if not export_path:
                continue

            try:
                with open(export_path) as f:
                    content = f.read()

                doc_match = re.search(
                    r"docs\.google\.com/document/d/([a-zA-Z0-9_-]+)",
                    content,
                )

                messages.append(
                    {
                        "thread_id": thread_info.get("thread_id", ""),
                        "subject": thread_info.get("subject", ""),
                        "content": content,
                        "doc_id": doc_match.group(1) if doc_match else None,
                        "file_path": export_path,
                    }
                )
            except Exception as e:
                logger.warning(f"Error reading {export_path}: {e}")

        return messages

    def get_calendar_event_by_id(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> dict[str, Any] | None:
        """Fetch a single calendar event by ID.

        Args:
            event_id: Event ID (plain or base64-encoded)
            calendar_id: Calendar ID

        Returns:
            Event dictionary or None if not found
        """
        # Handle base64-encoded event IDs
        try:
            decoded = base64.b64decode(event_id).decode("utf-8", errors="ignore")
            if " " in decoded:
                event_id = decoded.split()[0]
                logger.debug(f"Decoded base64 event ID to: {event_id}")
        except Exception:
            pass

        output_dir = self.config.gwt_output_dir / "calendar"
        output_dir.mkdir(parents=True, exist_ok=True)

        args = [
            "calendar",
            "--calendar",
            calendar_id,
            "--event-id",
            event_id,
            "--format",
            "json",
            "--output",
            str(output_dir),
        ]

        try:
            result = self._run_gwt(args, timeout=60, use_json=True)
        except Exception as e:
            logger.error(f"Failed to fetch event {event_id}: {e}")
            return None

        try:
            output_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GWT JSON output: {e}")
            return None

        if not output_data.get("success", False):
            logger.error("GWT command reported failure")
            for error in output_data.get("errors", []):
                logger.error(f"  {error}")
            return None

        events = output_data.get("events", [])
        if not events:
            logger.error(f"Event {event_id} not found")
            return None

        export_path = events[0].get("export_path")
        if not export_path:
            logger.error("No export path in response")
            return None

        try:
            with open(export_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {export_path}: {e}")
            return None

    def download_google_doc(
        self,
        doc_id: str,
        format: str = "md",
    ) -> str | None:
        """Download Google Doc content.

        Args:
            doc_id: Google Doc ID
            format: Output format (md, txt, etc.)

        Returns:
            Document content as string, or None on failure

        Note: This method loses embedded images! For docs with images,
        use download_google_doc_to_path() instead.
        """
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as f:
            output_path = Path(f.name)

        args = [
            "download",
            doc_id,
            "--format",
            format,
            "--output",
            str(output_path),
        ]

        try:
            result = self._run_gwt(args, timeout=60, use_json=True)

            output_data = json.loads(result.stdout)
            if not output_data.get("success", False):
                logger.warning(f"Download failed for {doc_id}")
                return None

            if output_path.exists():
                content = output_path.read_text()
                output_path.unlink()
                return content

            return None

        except Exception as e:
            logger.warning(f"Failed to download {doc_id}: {e}")
            if output_path.exists():
                output_path.unlink()
            return None

    def download_google_doc_to_path(
        self,
        doc_id: str,
        output_path: Path,
        format: str = "md",
    ) -> bool:
        """Download Google Doc directly to a path, preserving images.

        Args:
            doc_id: Google Doc ID
            output_path: Full path to save the document (e.g., /path/to/doc.md)
            format: Output format (md, txt, etc.)

        Returns:
            True if successful

        Note: Images are extracted to {output_path.parent}/images/
        """
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        args = [
            "download",
            doc_id,
            "--format",
            format,
            "--output",
            str(output_path),
        ]

        try:
            result = self._run_gwt(args, timeout=120, use_json=True)

            output_data = json.loads(result.stdout)
            if not output_data.get("success", False):
                logger.warning(f"Download failed for {doc_id}")
                return False

            return output_path.exists()

        except Exception as e:
            logger.warning(f"Failed to download {doc_id}: {e}")
            return False

    def download_drive_file(
        self,
        file_id: str,
        output_path: Path,
    ) -> bool:
        """Download file from Google Drive.

        Args:
            file_id: Drive file ID
            output_path: Local path to save file

        Returns:
            True if successful
        """
        args = [
            "download",
            file_id,
            "--output",
            str(output_path),
        ]

        try:
            result = self._run_gwt(args, timeout=120, use_json=True)

            output_data = json.loads(result.stdout)
            if output_data.get("success", False):
                return output_path.exists()

            return False

        except Exception as e:
            logger.warning(f"Failed to download {file_id}: {e}")
            return False

    def download_document(
        self,
        doc_id: str,
        output_path: Path,
        frontmatter: dict[str, str] | None = None,
    ) -> tuple[bool, str | None]:
        """Download Google Doc with optional frontmatter.

        Args:
            doc_id: Google Doc ID
            output_path: Local path to save file
            frontmatter: Optional frontmatter key-value pairs

        Returns:
            Tuple of (success, error_message)
        """
        args = [
            "download",
            doc_id,
            "--format",
            "md",
            "--output",
            str(output_path),
        ]

        if frontmatter:
            args.append("--enable-frontmatter")
            for key, value in frontmatter.items():
                args.extend(["-m", f"{key}={value}"])

        try:
            result = self._run_gwt(args, timeout=60, use_json=True)

            try:
                output_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                return False, f"Failed to parse GWT JSON output: {e}"

            if not output_data.get("success", False):
                errors = output_data.get("errors", [])
                error_msg = errors[0] if errors else "Unknown error"

                # Extract clean error message
                http_error_match = re.search(r'returned "([^"]+)"', error_msg)
                if http_error_match:
                    error_msg = http_error_match.group(1)

                return False, error_msg

            documents = output_data.get("documents", [])
            if documents and documents[0].get("files"):
                return True, None

            return False, "No files exported"

        except Exception as e:
            if hasattr(e, "gwt_error_message"):
                return False, e.gwt_error_message

            error_msg = str(e)
            http_error_match = re.search(r'returned "([^"]+)"', error_msg)
            if http_error_match:
                error_msg = http_error_match.group(1)
            elif "returned non-zero exit status" in error_msg:
                error_msg = "Download failed (permission denied or file not accessible)"

            return False, error_msg
