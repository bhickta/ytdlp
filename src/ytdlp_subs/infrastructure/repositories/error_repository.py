"""File-based implementation of error repository."""

import csv
from pathlib import Path
from typing import Optional

from ytdlp_subs.domain.models import VideoId
from ytdlp_subs.domain.repositories import IErrorRepository
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class FileErrorRepository(IErrorRepository):
    """File-based implementation of error repository."""

    def __init__(self, error_log_path: Optional[Path]) -> None:
        """
        Initialize the repository.

        Args:
            error_log_path: Path to the error log file (CSV)
        """
        self.error_log_path = error_log_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the error log file and parent directories exist."""
        if not self.error_log_path:
            return

        # Ensure parent directory exists
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file with headers if it doesn't exist
        if not self.error_log_path.exists():
            try:
                with open(self.error_log_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Video ID", "URL", "Error Type", "Error Message"])
            except Exception as e:
                logger.error("Failed to create error log file", error_path=str(self.error_log_path), error=str(e))

    def get_failed_video_ids(self) -> set[VideoId]:
        """
        Get all video IDs that have failed previously.

        Returns:
            Set of failed video IDs
        """
        failed_ids = set()

        if not self.error_log_path or not self.error_log_path.exists():
            return failed_ids

        try:
            with open(self.error_log_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    video_id_str = row.get("Video ID")
                    if video_id_str:
                        failed_ids.add(VideoId(video_id_str))
        except Exception as e:
            logger.error("Failed to read error log file", error_path=str(self.error_log_path), error=str(e))

        if failed_ids:
            logger.info("Loaded failed video IDs from error log", count=len(failed_ids))

        return failed_ids

    def record_error(self, video_id: VideoId, error_type: str, error_message: str) -> None:
        """
        Record a video processing error.

        Args:
            video_id: Video identifier
            error_type: Type/Class of the error
            error_message: Detailed error message
        """
        if not self.error_log_path:
            return

        try:
            # Check if this ID is already in the file to avoid duplicates
            existing_ids = self.get_failed_video_ids()
            if video_id in existing_ids:
                return

            with open(self.error_log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([str(video_id), video_id.url, error_type, error_message])

            logger.debug("Recorded error for video", video_id=str(video_id), error_type=error_type)
        except Exception as e:
            logger.error("Failed to write to error log file", error_path=str(self.error_log_path), error=str(e))
