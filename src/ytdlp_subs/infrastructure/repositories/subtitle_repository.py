"""File system-based subtitle repository implementation."""

import re
from pathlib import Path
from typing import Optional

from ytdlp_subs.domain.models import SubtitleFile, SubtitleFormat, SubtitleLanguage, VideoId
from ytdlp_subs.domain.repositories import ISubtitleRepository
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class FileSystemSubtitleRepository(ISubtitleRepository):
    """File system-based implementation of subtitle repository."""

    # Pattern to extract video ID from filename: optional_number_videoID_title.lang.ext
    VIDEO_ID_PATTERN = re.compile(r"^(?:\d+_)?([a-zA-Z0-9_-]{11})_.*")

    def __init__(self, output_dir: Path) -> None:
        """
        Initialize file system subtitle repository.

        Args:
            output_dir: Directory where subtitles are stored
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_subtitle(self, subtitle: SubtitleFile) -> None:
        """
        Save subtitle metadata (file should already exist on disk).

        Args:
            subtitle: Subtitle file to save

        Note:
            This is a no-op for file system repository as files are
            created directly by the download service.
        """
        logger.debug(
            "Subtitle saved",
            video_id=str(subtitle.video_id),
            language=subtitle.language.value,
            path=str(subtitle.file_path),
        )

    def get_subtitle(
        self,
        video_id: VideoId,
        language: str,
        format: str,
    ) -> Optional[SubtitleFile]:
        """
        Retrieve a subtitle file.

        Args:
            video_id: Video identifier
            language: Subtitle language
            format: Subtitle format

        Returns:
            SubtitleFile if found, None otherwise
        """
        pattern = f"*{video_id}*.{language}.{format}"
        matches = list(self.output_dir.glob(pattern))

        if not matches:
            logger.debug(
                "Subtitle not found",
                video_id=str(video_id),
                language=language,
                format=format,
            )
            return None

        file_path = matches[0]
        logger.debug(
            "Subtitle found",
            video_id=str(video_id),
            language=language,
            path=str(file_path),
        )

        return SubtitleFile(
            video_id=video_id,
            language=SubtitleLanguage(language),
            format=SubtitleFormat(format),
            file_path=file_path,
            size_bytes=file_path.stat().st_size,
        )

    def subtitle_exists(self, video_id: VideoId) -> bool:
        """
        Check if any subtitle exists for a video.

        Args:
            video_id: Video identifier

        Returns:
            True if subtitle exists
        """
        pattern = f"*{video_id}*"
        matches = list(self.output_dir.glob(pattern))
        exists = len(matches) > 0

        logger.debug(
            "Subtitle existence check",
            video_id=str(video_id),
            exists=exists,
            count=len(matches),
        )

        return exists

    def get_downloaded_video_ids(self) -> set[VideoId]:
        """
        Get all video IDs that have downloaded subtitles.

        Returns:
            Set of video IDs
        """
        if not self.output_dir.exists():
            logger.debug("Output directory does not exist", output_dir=str(self.output_dir))
            return set()

        logger.debug("Scanning output directory for downloaded videos")

        downloaded_ids: set[VideoId] = set()

        for file_path in self.output_dir.iterdir():
            if not file_path.is_file():
                continue

            match = self.VIDEO_ID_PATTERN.match(file_path.name)
            if match:
                try:
                    video_id = VideoId(match.group(1))
                    downloaded_ids.add(video_id)
                except ValueError:
                    logger.warning(
                        "Invalid video ID in filename",
                        filename=file_path.name,
                    )
                    continue

        logger.info(
            "Found downloaded videos",
            count=len(downloaded_ids),
            output_dir=str(self.output_dir),
        )

        return downloaded_ids
