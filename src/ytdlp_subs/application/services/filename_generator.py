"""Filename generator service."""

import re
from typing import Optional

from ytdlp_subs.domain.models import SubtitleFormat, SubtitleLanguage, VideoMetadata
from ytdlp_subs.domain.services import IFilenameGeneratorService
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class FilenameGenerator(IFilenameGeneratorService):
    """Service for generating subtitle filenames."""

    # Characters not allowed in filenames
    INVALID_CHARS_PATTERN = re.compile(r'[\\/*?:"<>|]')
    MAX_TITLE_LENGTH = 100

    def __init__(self, enable_numbering: bool = True) -> None:
        """
        Initialize filename generator.

        Args:
            enable_numbering: Whether to prepend sequential numbers
        """
        self.enable_numbering = enable_numbering

    def generate_filename(
        self,
        video_metadata: VideoMetadata,
        language: SubtitleLanguage,
        format: SubtitleFormat,
        index: Optional[int] = None,
        total_count: Optional[int] = None,
    ) -> str:
        """
        Generate a filename for a subtitle.

        Format: [index_]videoID_sanitizedTitle.language.format

        Args:
            video_metadata: Video metadata
            language: Subtitle language
            format: Subtitle format
            index: Optional sequential index
            total_count: Total count for padding calculation

        Returns:
            Generated filename
        """
        # Sanitize title
        safe_title = self._sanitize_title(video_metadata.title)

        # Build base name
        base_name = f"{video_metadata.video_id}_{safe_title}"

        # Add numbering prefix if enabled
        if self.enable_numbering and index is not None:
            prefix = self._generate_number_prefix(index, total_count)
            base_name = f"{prefix}_{base_name}"

        # Add language and format extension
        filename = f"{base_name}.{language.value}.{format.value}"

        logger.debug(
            "Generated filename",
            video_id=str(video_metadata.video_id),
            filename=filename,
        )

        return filename

    def _sanitize_title(self, title: str) -> str:
        """
        Sanitize title for use in filename.

        Args:
            title: Original title

        Returns:
            Sanitized title
        """
        # Remove invalid characters
        safe_title = self.INVALID_CHARS_PATTERN.sub("", title).strip()

        # Truncate to max length
        if len(safe_title) > self.MAX_TITLE_LENGTH:
            safe_title = safe_title[: self.MAX_TITLE_LENGTH]

        # Replace empty title
        if not safe_title:
            safe_title = "UnknownTitle"

        return safe_title

    def _generate_number_prefix(
        self,
        index: int,
        total_count: Optional[int] = None,
    ) -> str:
        """
        Generate zero-padded number prefix.

        Args:
            index: Current index
            total_count: Total count for padding calculation

        Returns:
            Zero-padded number string
        """
        if total_count is None:
            # Default padding
            return str(index).zfill(4)

        # Calculate padding based on total count
        padding = len(str(total_count))
        return str(index).zfill(padding)
