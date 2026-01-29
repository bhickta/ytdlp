"""File-based cache repository implementation."""

from pathlib import Path
from typing import Optional

from ytdlp_subs.domain.exceptions import CacheError
from ytdlp_subs.domain.models import VideoId
from ytdlp_subs.domain.repositories import ICacheRepository
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class FileCacheRepository(ICacheRepository):
    """File-based implementation of cache repository."""

    def __init__(self, cache_file: Optional[Path] = None) -> None:
        """
        Initialize file cache repository.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = cache_file

    def get_cached_video_ids(self) -> Optional[list[VideoId]]:
        """
        Retrieve cached video IDs from file.

        Returns:
            List of video IDs if cache exists and is valid, None otherwise
        """
        if not self.cache_file or not self.cache_file.exists():
            logger.debug("Cache file does not exist", cache_file=str(self.cache_file))
            return None

        try:
            logger.info("Loading video IDs from cache", cache_file=str(self.cache_file))

            with open(self.cache_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                logger.warning("Cache file is empty", cache_file=str(self.cache_file))
                return None

            video_ids = [VideoId(line) for line in lines]
            logger.info(
                "Loaded video IDs from cache",
                count=len(video_ids),
                cache_file=str(self.cache_file),
            )

            return video_ids

        except (IOError, OSError) as e:
            logger.error(
                "Failed to read cache file",
                cache_file=str(self.cache_file),
                error=str(e),
            )
            raise CacheError(
                f"Failed to read cache file: {e}",
                cache_file=str(self.cache_file),
            ) from e

        except ValueError as e:
            logger.error(
                "Invalid video ID in cache file",
                cache_file=str(self.cache_file),
                error=str(e),
            )
            raise CacheError(
                f"Invalid video ID in cache: {e}",
                cache_file=str(self.cache_file),
            ) from e

    def save_video_ids(self, video_ids: list[VideoId]) -> None:
        """
        Save video IDs to cache file.

        Args:
            video_ids: List of video IDs to cache

        Raises:
            CacheError: If save operation fails
        """
        if not self.cache_file:
            logger.debug("No cache file configured, skipping save")
            return

        try:
            # Ensure parent directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            logger.info(
                "Saving video IDs to cache",
                count=len(video_ids),
                cache_file=str(self.cache_file),
            )

            with open(self.cache_file, "w", encoding="utf-8") as f:
                for video_id in video_ids:
                    f.write(f"{video_id}\n")

            logger.info(
                "Successfully saved video IDs to cache",
                count=len(video_ids),
                cache_file=str(self.cache_file),
            )

        except (IOError, OSError) as e:
            logger.error(
                "Failed to write cache file",
                cache_file=str(self.cache_file),
                error=str(e),
            )
            raise CacheError(
                f"Failed to write cache file: {e}",
                cache_file=str(self.cache_file),
            ) from e

    def clear_cache(self) -> None:
        """
        Clear cache file.

        Raises:
            CacheError: If clear operation fails
        """
        if not self.cache_file or not self.cache_file.exists():
            logger.debug("No cache file to clear")
            return

        try:
            logger.info("Clearing cache", cache_file=str(self.cache_file))
            self.cache_file.unlink()
            logger.info("Cache cleared successfully", cache_file=str(self.cache_file))

        except (IOError, OSError) as e:
            logger.error(
                "Failed to clear cache file",
                cache_file=str(self.cache_file),
                error=str(e),
            )
            raise CacheError(
                f"Failed to clear cache file: {e}",
                cache_file=str(self.cache_file),
            ) from e

    def cache_exists(self) -> bool:
        """
        Check if cache file exists.

        Returns:
            True if cache file exists
        """
        exists = self.cache_file is not None and self.cache_file.exists()
        logger.debug("Cache exists check", exists=exists, cache_file=str(self.cache_file))
        return exists
