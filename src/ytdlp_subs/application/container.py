"""Dependency injection container using Factory pattern."""

from pathlib import Path
from typing import Optional

from ytdlp_subs.application.services.file_processor import SubtitleFileProcessor
from ytdlp_subs.application.services.filename_generator import FilenameGenerator
from ytdlp_subs.application.services.subtitle_downloader import YtDlpSubtitleDownloader
from ytdlp_subs.application.use_cases.download_orchestrator import DownloadOrchestrator
from ytdlp_subs.domain.models import SubtitleFormat
from ytdlp_subs.infrastructure.command_executor import CommandExecutor
from ytdlp_subs.infrastructure.config import AppConfig
from ytdlp_subs.infrastructure.repositories import (
    FileCacheRepository,
    FileSystemSubtitleRepository,
    YtDlpVideoRepository,
)


class Container:
    """
    Dependency injection container.

    Follows the Factory pattern to create and wire up all dependencies.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize container with configuration.

        Args:
            config: Application configuration
        """
        self.config = config

        # Ensure output directory exists
        self.config.ensure_output_dir()

        # Initialize infrastructure
        self._command_executor: Optional[CommandExecutor] = None
        self._cache_repository: Optional[FileCacheRepository] = None
        self._video_repository: Optional[YtDlpVideoRepository] = None
        self._subtitle_repository: Optional[FileSystemSubtitleRepository] = None

        # Initialize services
        self._subtitle_downloader: Optional[YtDlpSubtitleDownloader] = None
        self._file_processor: Optional[SubtitleFileProcessor] = None
        self._filename_generator: Optional[FilenameGenerator] = None

        # Initialize use cases
        self._download_orchestrator: Optional[DownloadOrchestrator] = None

    @property
    def command_executor(self) -> CommandExecutor:
        """Get or create command executor."""
        if self._command_executor is None:
            self._command_executor = CommandExecutor(timeout=300)  # 5 minute timeout
        return self._command_executor

    @property
    def cache_repository(self) -> FileCacheRepository:
        """Get or create cache repository."""
        if self._cache_repository is None:
            cache_file = self.config.get_cache_path()
            self._cache_repository = FileCacheRepository(cache_file=cache_file)
        return self._cache_repository

    @property
    def video_repository(self) -> YtDlpVideoRepository:
        """Get or create video repository."""
        if self._video_repository is None:
            self._video_repository = YtDlpVideoRepository(
                command_executor=self.command_executor,
                cookies_from_browser=self.config.cookies_from_browser,
            )
        return self._video_repository

    @property
    def subtitle_repository(self) -> FileSystemSubtitleRepository:
        """Get or create subtitle repository."""
        if self._subtitle_repository is None:
            self._subtitle_repository = FileSystemSubtitleRepository(
                output_dir=self.config.output_dir,
            )
        return self._subtitle_repository

    @property
    def subtitle_downloader(self) -> YtDlpSubtitleDownloader:
        """Get or create subtitle downloader."""
        if self._subtitle_downloader is None:
            self._subtitle_downloader = YtDlpSubtitleDownloader(
                command_executor=self.command_executor,
                cookies_from_browser=self.config.cookies_from_browser,
            )
        return self._subtitle_downloader

    @property
    def file_processor(self) -> SubtitleFileProcessor:
        """Get or create file processor."""
        if self._file_processor is None:
            self._file_processor = SubtitleFileProcessor()
        return self._file_processor

    @property
    def filename_generator(self) -> FilenameGenerator:
        """Get or create filename generator."""
        if self._filename_generator is None:
            self._filename_generator = FilenameGenerator(
                enable_numbering=self.config.enable_numbering,
            )
        return self._filename_generator

    @property
    def download_orchestrator(self) -> DownloadOrchestrator:
        """Get or create download orchestrator."""
        if self._download_orchestrator is None:
            # Determine output format
            output_format = SubtitleFormat.TXT if self.config.clean_txt else None

            self._download_orchestrator = DownloadOrchestrator(
                video_repository=self.video_repository,
                subtitle_repository=self.subtitle_repository,
                cache_repository=self.cache_repository,
                subtitle_downloader=self.subtitle_downloader,
                file_processor=self.file_processor,
                filename_generator=self.filename_generator,
                language_preferences=self.config.get_languages(),
                min_wait_seconds=self.config.min_wait_seconds,
                max_wait_seconds=self.config.max_wait_seconds,
                output_format=output_format,
                force_refresh=self.config.force_refresh,
            )
        return self._download_orchestrator
