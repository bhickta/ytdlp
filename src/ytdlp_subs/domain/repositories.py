"""Repository interfaces following the Repository pattern."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ytdlp_subs.domain.models import SubtitleFile, VideoId, VideoMetadata


class IVideoRepository(ABC):
    """Interface for video data access."""

    @abstractmethod
    def get_video_metadata(self, video_id: VideoId) -> Optional[VideoMetadata]:
        """
        Retrieve video metadata.

        Args:
            video_id: Video identifier

        Returns:
            VideoMetadata if found, None otherwise
        """
        pass

    @abstractmethod
    def get_channel_video_ids(self, channel_url: str) -> list[VideoId]:
        """
        Retrieve all video IDs from a channel.

        Args:
            channel_url: YouTube channel URL

        Returns:
            List of video IDs
        """
        pass


class ISubtitleRepository(ABC):
    """Interface for subtitle data access."""

    @abstractmethod
    def save_subtitle(self, subtitle: SubtitleFile) -> None:
        """
        Save a subtitle file.

        Args:
            subtitle: Subtitle file to save
        """
        pass

    @abstractmethod
    def get_subtitle(
        self, video_id: VideoId, language: str, format: str
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
        pass

    @abstractmethod
    def subtitle_exists(self, video_id: VideoId) -> bool:
        """
        Check if any subtitle exists for a video.

        Args:
            video_id: Video identifier

        Returns:
            True if subtitle exists
        """
        pass

    @abstractmethod
    def get_downloaded_video_ids(self) -> set[VideoId]:
        """
        Get all video IDs that have downloaded subtitles.

        Returns:
            Set of video IDs
        """
        pass


class ICacheRepository(ABC):
    """Interface for cache data access."""

    @abstractmethod
    def get_cached_video_ids(self) -> Optional[list[VideoId]]:
        """
        Retrieve cached video IDs.

        Returns:
            List of video IDs if cache exists, None otherwise
        """
        pass

    @abstractmethod
    def save_video_ids(self, video_ids: list[VideoId]) -> None:
        """
        Save video IDs to cache.

        Args:
            video_ids: List of video IDs to cache
        """
        pass

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear all cached data."""
        pass

    @abstractmethod
    def cache_exists(self) -> bool:
        """
        Check if cache exists.

        Returns:
            True if cache exists
        """
        pass
