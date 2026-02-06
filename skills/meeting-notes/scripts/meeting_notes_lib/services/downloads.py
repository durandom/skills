"""
Download Service - Download meeting assets from Google Workspace.

Downloads Gemini transcripts, summaries, and calendar attachments
to the local filesystem.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..models import Meeting
from ..repositories import MeetingRepository

logger = logging.getLogger(__name__)


@dataclass
class FailedDownload:
    """Record of a failed download."""

    file_id: str
    title: str
    url: str
    error: str


@dataclass
class DownloadResult:
    """Result of downloading a single meeting's assets."""

    meeting: Meeting
    success: bool
    files_downloaded: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DownloadSummary:
    """Summary of a download batch."""

    total: int
    successful: int
    failed: int
    failed_downloads: list[FailedDownload] = field(default_factory=list)
    downloaded_files: list[str] = field(default_factory=list)


class DownloadService:
    """Service for downloading meeting assets.

    Downloads:
    - Gemini transcripts (Google Docs -> Markdown)
    - Gemini summaries (Google Docs -> Markdown)
    - Calendar attachments (various formats)
    - Linked documents found in downloaded content
    """

    # Mime type prefixes to exclude from downloads (e.g., large video files)
    EXCLUDED_MIME_PREFIXES = (
        "video/",  # Google Meet recordings can be 500MB+
    )

    # Map mime types to file extensions
    # INTENT: gwt interprets paths without extensions as directories, so we
    # must add them
    MIME_TO_EXTENSION = {
        # Google Workspace types (exported as markdown)
        "application/vnd.google-apps.document": ".md",
        "application/vnd.google-apps.spreadsheet": ".md",
        "application/vnd.google-apps.presentation": ".pdf",
        # Common file types
        "text/plain": ".txt",
        "text/markdown": ".md",
        "text/html": ".html",
        "application/pdf": ".pdf",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "application/json": ".json",
    }

    def __init__(
        self,
        gwt,  # GWTInvoker - not typed to avoid circular import
        meeting_repo: MeetingRepository,
        output_dir: Path,
        config: dict[str, Any],
    ):
        """Initialize download service.

        Args:
            gwt: GWTInvoker instance for API calls
            meeting_repo: Repository for meeting records
            output_dir: Base directory for meeting output (repo root)
            config: Configuration dict with user_email, etc.
        """
        self.gwt = gwt
        self.meeting_repo = meeting_repo
        self.output_dir = Path(output_dir)
        self.config = config
        self.failed_downloads: list[FailedDownload] = []

    def get_ready_for_download(self) -> list[Meeting]:
        """Get meetings ready for asset download."""
        return self.meeting_repo.get_ready_for_download()

    def _is_shared_attachment(self, file_id: str, title: str, meeting: Meeting) -> bool:
        """Determine if an attachment is shared (series-level) vs date-specific.

        Shared attachments go to the series folder (e.g., meetings/rhdh/meeting-name/).
        Date-specific attachments go to the instance folder (e.g., .../2026-01-08/).

        Detection rules:
        1. If file_id appears in calendar description → shared (agenda doc)
        2. If title contains meeting date → date-specific (recording, chat)
        3. If title is "Notes by Gemini" → date-specific
        4. Default: shared for recurring, date-specific for one-off
        """
        # Check if file_id is linked in the calendar description
        if meeting.calendar_metadata and meeting.calendar_metadata.description:
            if file_id in meeting.calendar_metadata.description:
                logger.debug("    → SHARED (file_id in description)")
                return True

        # Check if title contains the meeting date (various formats)
        if meeting.date:
            date_variants = [
                meeting.date,  # 2026-01-08
                meeting.date.replace("-", "/"),  # 2026/01/08
                meeting.date.replace("-", "_"),  # 2026_01_08
            ]
            for variant in date_variants:
                if variant in title:
                    logger.debug(f"    → DATE-SPECIFIC (date {variant!r} in title)")
                    return False

        # Gemini notes are always date-specific
        if "Notes by Gemini" in title or "Gemini" in title:
            logger.debug("    → DATE-SPECIFIC (Gemini notes)")
            return False

        # Default: shared for recurring meetings
        if meeting.is_recurring:
            logger.debug("    → SHARED (default for recurring)")
            return True

        logger.debug("    → DATE-SPECIFIC (default)")
        return False

    def download_meeting(
        self,
        meeting: Meeting,
        dry_run: bool = False,
        force: bool = False,
    ) -> DownloadResult:
        """Download assets for a single meeting.

        Args:
            meeting: Meeting to download assets for
            dry_run: If True, don't actually download
            force: If True, re-download existing files

        Returns:
            DownloadResult with status and downloaded files
        """
        result = DownloadResult(meeting=meeting, success=True)

        if not meeting.directory:
            result.success = False
            result.errors.append("Meeting has no directory path set")
            return result

        meeting_dir = self.output_dir / meeting.directory

        if not dry_run:
            meeting_dir.mkdir(parents=True, exist_ok=True)

        # Download transcript
        if meeting.gemini_assets and meeting.gemini_assets.transcript:
            transcript_path = meeting_dir / "gemini-transcript.md"
            if force or not transcript_path.exists():
                success = self._download_google_doc(
                    meeting.gemini_assets.transcript.document_id,
                    transcript_path,
                    "transcript",
                    dry_run,
                )
                if success:
                    result.files_downloaded.append(str(transcript_path))
                else:
                    result.errors.append("Failed to download transcript")

        # Download summary
        if meeting.gemini_assets and meeting.gemini_assets.summary:
            summary_path = meeting_dir / "gemini-summary.md"
            if force or not summary_path.exists():
                success = self._download_google_doc(
                    meeting.gemini_assets.summary.document_id,
                    summary_path,
                    "summary",
                    dry_run,
                )
                if success:
                    result.files_downloaded.append(str(summary_path))
                else:
                    result.errors.append("Failed to download summary")

        # Download calendar attachments
        if meeting.calendar_metadata and meeting.calendar_metadata.calendar_attachments:
            attachment_count = len(meeting.calendar_metadata.calendar_attachments)
            logger.debug(f"  Processing {attachment_count} calendar attachment(s)")

            # For recurring meetings, calculate series directory (parent of dated
            # folder). E.g., meetings/rhdh/meeting-slug/2026-01-08 →
            # meetings/rhdh/meeting-slug
            series_dir = meeting_dir.parent if meeting.is_recurring else meeting_dir

            for i, att in enumerate(meeting.calendar_metadata.calendar_attachments, 1):
                file_id = att.get("file_id", "")
                title = att.get("title", "attachment")
                mime_type = att.get("mime_type", "unknown")
                logger.debug(
                    f"  Attachment [{i}]: title={title!r}, mime={mime_type}, "
                    f"file_id={file_id}"
                )

                # Skip excluded mime types (e.g., video recordings)
                if any(
                    mime_type.startswith(prefix)
                    for prefix in self.EXCLUDED_MIME_PREFIXES
                ):
                    logger.debug(
                        f"  Attachment [{i}]: SKIPPED (excluded mime type: {mime_type})"
                    )
                    continue

                if file_id:
                    # Build filename with appropriate extension
                    safe_name = self._safe_filename(title)
                    extension = self.MIME_TO_EXTENSION.get(mime_type, "")
                    if extension and not safe_name.endswith(extension):
                        safe_name = safe_name + extension

                    # Determine target directory: series folder or instance folder
                    is_shared = self._is_shared_attachment(file_id, title, meeting)
                    target_dir = series_dir if is_shared else meeting_dir
                    att_path = target_dir / safe_name
                    logger.debug(f"  Attachment [{i}]: target path={att_path}")

                    # Ensure target directory exists
                    if not dry_run:
                        target_dir.mkdir(parents=True, exist_ok=True)

                    if force or not att_path.exists():
                        # Use appropriate download method based on mime type
                        if mime_type.startswith("application/vnd.google-apps."):
                            # Google Workspace document - export as markdown
                            success = self._download_google_doc(
                                file_id, att_path, title, dry_run
                            )
                        else:
                            # Regular file - download as-is
                            success = self._download_drive_file(
                                file_id, att_path, title, dry_run
                            )
                        if success:
                            result.files_downloaded.append(str(att_path))

        # Generate metadata files
        if not dry_run:
            self._generate_readme(meeting, meeting_dir)
            self._generate_metadata(meeting, meeting_dir)
            result.files_downloaded.append(str(meeting_dir / "README.md"))
            result.files_downloaded.append(str(meeting_dir / "metadata.json"))

        # Update meeting status
        if result.success and not dry_run:
            self.meeting_repo.mark_synced(meeting.stable_id, meeting.directory)

        return result

    def download_all(
        self,
        meetings: list[Meeting] | None = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> DownloadSummary:
        """Download assets for multiple meetings.

        Args:
            meetings: List of meetings to download. If None, uses ready_for_download.
            dry_run: If True, don't actually download
            force: If True, re-download existing files

        Returns:
            DownloadSummary with statistics
        """
        if meetings is None:
            meetings = self.get_ready_for_download()

        self.failed_downloads.clear()

        successful = 0
        failed = 0
        all_downloaded_files: list[str] = []

        for i, meeting in enumerate(meetings, 1):
            # Log progress
            asset_desc = self._describe_assets(meeting)
            emoji = (
                "👥"
                if meeting.is_one_on_one
                else ("🔁" if meeting.is_recurring else "📅")
            )
            logger.info(f"[{i}/{len(meetings)}] {emoji} {meeting.title} ({asset_desc})")

            result = self.download_meeting(meeting, dry_run, force)

            if result.success:
                successful += 1
                all_downloaded_files.extend(result.files_downloaded)
            else:
                failed += 1
                for error in result.errors:
                    logger.warning(f"  Error: {error}")

        logger.info(f"Download complete: {successful} successful, {failed} failed")

        return DownloadSummary(
            total=len(meetings),
            successful=successful,
            failed=failed,
            failed_downloads=self.failed_downloads.copy(),
            downloaded_files=all_downloaded_files,
        )

    def _download_google_doc(
        self,
        doc_id: str,
        output_path: Path,
        title: str,
        dry_run: bool,
    ) -> bool:
        """Download a Google Doc as Markdown, preserving embedded images.

        Images are extracted to {output_path.parent}/images/
        """
        logger.debug(f"  [download_google_doc] doc_id={doc_id}")
        logger.debug(f"  [download_google_doc] output_path={output_path}")
        logger.debug(f"  [download_google_doc] title={title}")

        if dry_run:
            logger.info(f"  Would download: {title} -> {output_path}")
            return True

        try:
            # Use download_google_doc_to_path to preserve images
            success = self.gwt.download_google_doc_to_path(
                doc_id, output_path, format="md"
            )
            if success:
                size = output_path.stat().st_size if output_path.exists() else 0
                logger.info(f"  ✓ {title} ({size} bytes) → {output_path}")
                return True
            else:
                self.failed_downloads.append(
                    FailedDownload(
                        file_id=doc_id,
                        title=title,
                        url=f"https://docs.google.com/document/d/{doc_id}/edit",
                        error="Download failed",
                    )
                )
                return False
        except Exception as e:
            self.failed_downloads.append(
                FailedDownload(
                    file_id=doc_id,
                    title=title,
                    url=f"https://docs.google.com/document/d/{doc_id}/edit",
                    error=str(e),
                )
            )
            logger.warning(f"  Failed to download {title}: {e}")
            return False

    def _download_drive_file(
        self,
        file_id: str,
        output_path: Path,
        title: str,
        dry_run: bool,
    ) -> bool:
        """Download a file from Google Drive."""
        logger.debug(f"  [download_drive_file] file_id={file_id}")
        logger.debug(f"  [download_drive_file] output_path={output_path}")
        logger.debug(f"  [download_drive_file] title={title}")

        if dry_run:
            logger.info(f"  Would download: {title} -> {output_path}")
            return True

        try:
            # Use gwt to download the file
            success = self.gwt.download_drive_file(file_id, output_path)
            if success:
                size = output_path.stat().st_size if output_path.exists() else 0
                logger.info(f"  ✓ {title} ({size} bytes) → {output_path}")
                return True
            else:
                self.failed_downloads.append(
                    FailedDownload(
                        file_id=file_id,
                        title=title,
                        url=f"https://drive.google.com/file/d/{file_id}/view",
                        error="Download failed",
                    )
                )
                return False
        except Exception as e:
            self.failed_downloads.append(
                FailedDownload(
                    file_id=file_id,
                    title=title,
                    url=f"https://drive.google.com/file/d/{file_id}/view",
                    error=str(e),
                )
            )
            logger.warning(f"  Failed to download {title}: {e}")
            return False

    def _generate_readme(self, meeting: Meeting, meeting_dir: Path) -> None:
        """Generate README.md with meeting metadata."""
        lines = [
            f"# {meeting.title}",
            "",
            f"**Date:** {meeting.date}",
        ]

        if meeting.time:
            lines.append(f"**Time:** {meeting.time}")

        if meeting.calendar_metadata:
            if meeting.calendar_metadata.attendee_count:
                lines.append(
                    f"**Attendees:** {meeting.calendar_metadata.attendee_count}"
                )
            if meeting.calendar_metadata.calendar_link:
                calendar_link = meeting.calendar_metadata.calendar_link
                lines.append(f"**Calendar:** [View Event]({calendar_link})")

        lines.append("")

        # Links to Gemini assets
        if meeting.gemini_assets:
            lines.append("## Meeting Notes")
            lines.append("")
            if meeting.gemini_assets.transcript:
                lines.append("- [Gemini Transcript](gemini-transcript.md)")
            if meeting.gemini_assets.summary:
                lines.append("- [Gemini Summary](gemini-summary.md)")
            lines.append("")

        # Description
        if meeting.calendar_metadata and meeting.calendar_metadata.description:
            lines.append("## Description")
            lines.append("")
            lines.append(meeting.calendar_metadata.description)
            lines.append("")

        readme_path = meeting_dir / "README.md"
        readme_path.write_text("\n".join(lines))

    def _generate_metadata(self, meeting: Meeting, meeting_dir: Path) -> None:
        """Generate metadata.json with structured meeting data."""
        metadata = {
            "stable_id": meeting.stable_id,
            "event_id": meeting.event_id,
            "title": meeting.title,
            "date": meeting.date,
            "time": meeting.time,
            "slug": meeting.slug,
            "tag": meeting.tag,
            "is_recurring": meeting.is_recurring,
            "is_one_on_one": meeting.is_one_on_one,
            "directory": meeting.directory,
        }

        if meeting.calendar_metadata:
            metadata["attendee_count"] = meeting.calendar_metadata.attendee_count
            metadata["has_video_conference"] = (
                meeting.calendar_metadata.has_video_conference
            )
            metadata["calendar_link"] = meeting.calendar_metadata.calendar_link

        if meeting.gemini_assets:
            metadata["gemini_assets"] = meeting.gemini_assets.to_dict()

        metadata_path = meeting_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _describe_assets(self, meeting: Meeting) -> str:
        """Generate description of meeting assets for logging."""
        parts = []
        if meeting.gemini_assets:
            if meeting.gemini_assets.transcript:
                parts.append("transcript")
            if meeting.gemini_assets.summary:
                parts.append("summary")
        if meeting.calendar_metadata and meeting.calendar_metadata.calendar_attachments:
            count = len(meeting.calendar_metadata.calendar_attachments)
            parts.append(f"{count} attachment{'s' if count != 1 else ''}")

        return ", ".join(parts) if parts else "no assets"

    def _safe_filename(self, title: str) -> str:
        """Convert title to safe filename."""
        import re

        # Remove or replace unsafe characters
        safe = re.sub(r'[<>:"/\\|?*]', "-", title)
        safe = re.sub(r"-+", "-", safe)
        return safe.strip("-")[:100]
