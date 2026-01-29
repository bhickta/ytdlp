"""Service interfaces for domain operations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ytdlp_subs.domain.models import (
    SubtitleFile,
    SubtitleFormat,
    SubtitleLanguage,
    VideoId,
    VideoMetadata,
)


class IVideoFetcherService(ABC):
    """Interface for fetching video information."""

    @abstractmethod
    def fetch_channel_videos(self, channel_url: str) -> list[VideoId]:
        """
        Fetch all video IDs from a channel.

        Args:
            channel_url: YouTube channel URL

        Returns:
            List of video IDs
        """
        pass

    @abstractmethod
    def fetch_video_metadata(self, video_id: VideoId) -> VideoMetadata:
        """
        Fetch metadata for a specific video.

        Args:
            video_id: Video identifier

        Returns:
            Video metadata
        """
        pass


class ISubtitleDownloaderService(ABC):
    """Interface for downloading subtitles."""

    @abstractmethod
    def download_subtitle(
        self,
        video_id: VideoId,
        language: SubtitleLanguage,
        output_dir: Path,
    ) -> Optional[SubtitleFile]:
        """
        Download subtitle for a video.

        Args:
            video_id: Video identifier
            language: Desired subtitle language
            output_dir: Directory to save subtitle

        Returns:
            SubtitleFile if successful, None otherwise
        """
        pass


class IFileProcessorService(ABC):
    """Interface for processing subtitle files."""

    @abstractmethod
    def process_file(
        self,
        input_file: Path,
        output_format: Optional[SubtitleFormat] = None,
    ) -> Path:
        """
        Process a subtitle file.

        Args:
            input_file: Input file path
            output_format: Desired output format

        Returns:
            Path to processed file
        """
        pass

    @abstractmethod
    def clean_vtt_to_txt(self, vtt_file: Path) -> Path:
        """
        Convert VTT file to clean text.

        Args:
            vtt_file: VTT file path

        Returns:
            Path to cleaned text file
        """
        pass


class IFilenameGeneratorService(ABC):
    """Interface for generating filenames."""

    @abstractmethod
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

        Args:
            video_metadata: Video metadata
            language: Subtitle language
            format: Subtitle format
            index: Optional sequential index
            total_count: Total count for padding calculation

        Returns:
            Generated filename
        """
        pass
