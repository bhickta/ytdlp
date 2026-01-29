"""Download orchestrator use case - coordinates the entire download process."""

import random
import time
from typing import Callable, Optional

from ytdlp_subs.domain.exceptions import DownloadError
from ytdlp_subs.domain.models import (
    DownloadProgress,
    SubtitleFormat,
    SubtitleLanguage,
    VideoId,
    VideoMetadata,
)
from ytdlp_subs.domain.repositories import ICacheRepository, ISubtitleRepository, IVideoRepository
from ytdlp_subs.domain.services import (
    IFileProcessorService,
    IFilenameGeneratorService,
    ISubtitleDownloaderService,
)
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class DownloadOrchestrator:
    """
    Orchestrates the subtitle download process.

    This is the main use case that coordinates all services and repositories
    to download subtitles from a YouTube channel.
    """

    def __init__(
        self,
        video_repository: IVideoRepository,
        subtitle_repository: ISubtitleRepository,
        cache_repository: ICacheRepository,
        subtitle_downloader: ISubtitleDownloaderService,
        file_processor: IFileProcessorService,
        filename_generator: IFilenameGeneratorService,
        language_preferences: list[SubtitleLanguage],
        min_wait_seconds: float = 5.0,
        max_wait_seconds: float = 15.0,
        output_format: Optional[SubtitleFormat] = None,
        force_refresh: bool = False,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
    ) -> None:
        """
        Initialize download orchestrator.

        Args:
            video_repository: Repository for video data
            subtitle_repository: Repository for subtitle data
            cache_repository: Repository for cache data
            subtitle_downloader: Service for downloading subtitles
            file_processor: Service for processing files
            filename_generator: Service for generating filenames
            language_preferences: Ordered list of preferred languages
            min_wait_seconds: Minimum wait time between downloads
            max_wait_seconds: Maximum wait time between downloads
            output_format: Optional output format for processing
            force_refresh: Whether to force refresh cache
            progress_callback: Optional callback for progress updates
        """
        self.video_repository = video_repository
        self.subtitle_repository = subtitle_repository
        self.cache_repository = cache_repository
        self.subtitle_downloader = subtitle_downloader
        self.file_processor = file_processor
        self.filename_generator = filename_generator
        self.language_preferences = language_preferences
        self.min_wait_seconds = min_wait_seconds
        self.max_wait_seconds = max_wait_seconds
        self.output_format = output_format
        self.force_refresh = force_refresh
        self.progress_callback = progress_callback

    def execute(self, channel_url: str, output_dir) -> DownloadProgress:
        """
        Execute the download process for a channel.

        Args:
            channel_url: YouTube channel URL
            output_dir: Directory to save subtitles

        Returns:
            Final download progress
        """
        logger.info("Starting download process", channel_url=channel_url)

        # Get all video IDs from channel (with caching)
        all_video_ids = self._get_channel_videos(channel_url)

        if not all_video_ids:
            logger.warning("No videos found in channel")
            return DownloadProgress(
                total_videos=0,
                processed_videos=0,
                skipped_videos=0,
                failed_videos=0,
            )

        # Get already downloaded video IDs
        downloaded_ids = self.subtitle_repository.get_downloaded_video_ids()

        # Filter out already downloaded videos
        videos_to_download = [vid for vid in all_video_ids if vid not in downloaded_ids]

        # Initialize progress
        progress = DownloadProgress(
            total_videos=len(all_video_ids),
            processed_videos=0,
            skipped_videos=len(downloaded_ids),
            failed_videos=0,
        )

        logger.info(
            "Download plan",
            total_videos=progress.total_videos,
            already_downloaded=progress.skipped_videos,
            to_download=len(videos_to_download),
        )

        if not videos_to_download:
            logger.info("All videos already downloaded")
            return progress

        # Process each video
        for idx, video_id in enumerate(videos_to_download, start=1):
            progress.current_video = video_id

            try:
                self._process_video(
                    video_id=video_id,
                    output_dir=output_dir,
                    current_index=idx + progress.skipped_videos,
                    total_count=progress.total_videos,
                )

                progress.processed_videos += 1

            except Exception as e:
                logger.error(
                    "Failed to process video",
                    video_id=str(video_id),
                    error=str(e),
                )
                progress.failed_videos += 1

            # Report progress
            if self.progress_callback:
                self.progress_callback(progress)

            # Wait between downloads (except for last video)
            if idx < len(videos_to_download):
                self._wait_random_time()

        logger.info(
            "Download process completed",
            total=progress.total_videos,
            processed=progress.processed_videos,
            skipped=progress.skipped_videos,
            failed=progress.failed_videos,
            success_rate=f"{progress.success_rate:.1f}%",
        )

        return progress

    def _get_channel_videos(self, channel_url: str) -> list[VideoId]:
        """Get channel videos with caching support."""
        # Try cache first if not forcing refresh
        if not self.force_refresh:
            cached_ids = self.cache_repository.get_cached_video_ids()
            if cached_ids:
                logger.info("Using cached video IDs", count=len(cached_ids))
                return cached_ids

        # Fetch from network
        logger.info("Fetching video IDs from network")
        video_ids = self.video_repository.get_channel_video_ids(channel_url)

        # Save to cache
        self.cache_repository.save_video_ids(video_ids)

        return video_ids

    def _process_video(
        self,
        video_id: VideoId,
        output_dir,
        current_index: int,
        total_count: int,
    ) -> None:
        """Process a single video."""
        logger.info(
            "Processing video",
            video_id=str(video_id),
            index=current_index,
            total=total_count,
        )

        # Try each language preference
        for language in self.language_preferences:
            logger.debug(
                "Attempting language",
                video_id=str(video_id),
                language=language.value,
            )

            subtitle_file = self.subtitle_downloader.download_subtitle(
                video_id=video_id,
                language=language,
                output_dir=output_dir,
            )

            if subtitle_file is None:
                logger.debug(
                    "Subtitle not available",
                    video_id=str(video_id),
                    language=language.value,
                )
                continue

            # Get video metadata for filename generation
            metadata = self.video_repository.get_video_metadata(video_id)
            if metadata is None:
                metadata = VideoMetadata(video_id=video_id, title="UnknownTitle")

            # Generate final filename
            final_filename = self.filename_generator.generate_filename(
                video_metadata=metadata,
                language=language,
                format=subtitle_file.format,
                index=current_index,
                total_count=total_count,
            )

            final_path = output_dir / final_filename

            # Rename file
            subtitle_file.file_path.rename(final_path)
            subtitle_file.file_path = final_path

            logger.info(
                "Renamed subtitle file",
                video_id=str(video_id),
                filename=final_filename,
            )

            # Process file if needed
            if self.output_format:
                processed_path = self.file_processor.process_file(
                    input_file=final_path,
                    output_format=self.output_format,
                )
                subtitle_file.file_path = processed_path

            # Save to repository
            self.subtitle_repository.save_subtitle(subtitle_file)

            logger.info(
                "Successfully processed video",
                video_id=str(video_id),
                language=language.value,
                final_path=str(subtitle_file.file_path),
            )

            # Success - don't try other languages
            return

        # If we get here, no subtitle was found in any language
        logger.warning(
            "No subtitles found in any preferred language",
            video_id=str(video_id),
            languages=[lang.value for lang in self.language_preferences],
        )

    def _wait_random_time(self) -> None:
        """Wait a random time between min and max wait seconds."""
        wait_time = random.uniform(self.min_wait_seconds, self.max_wait_seconds)
        logger.debug("Waiting between downloads", wait_seconds=f"{wait_time:.2f}")
        time.sleep(wait_time)
