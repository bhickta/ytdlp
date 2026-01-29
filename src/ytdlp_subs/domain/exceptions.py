"""Domain exceptions for the subtitle downloader."""

from typing import Any


class SubtitleDownloaderError(Exception):
    """Base exception for all subtitle downloader errors."""

    def __init__(self, message: str, **context: Any) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            **context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.context = context


class VideoFetchError(SubtitleDownloaderError):
    """Raised when video information cannot be fetched."""

    pass


class SubtitleNotFoundError(SubtitleDownloaderError):
    """Raised when requested subtitle language is not available."""

    pass


class DownloadError(SubtitleDownloaderError):
    """Raised when subtitle download fails."""

    pass


class FileProcessingError(SubtitleDownloaderError):
    """Raised when file processing fails."""

    pass


class ConfigurationError(SubtitleDownloaderError):
    """Raised when configuration is invalid."""

    pass


class CacheError(SubtitleDownloaderError):
    """Raised when cache operations fail."""

    pass


class ValidationError(SubtitleDownloaderError):
    """Raised when data validation fails."""

    pass


class CommandExecutionError(SubtitleDownloaderError):
    """Raised when external command execution fails."""

    pass
