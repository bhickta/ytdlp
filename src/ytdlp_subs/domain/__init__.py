"""Domain layer initialization."""

from ytdlp_subs.domain.exceptions import (
    CacheError,
    CommandExecutionError,
    ConfigurationError,
    DownloadError,
    FileProcessingError,
    SubtitleDownloaderError,
    SubtitleNotFoundError,
    ValidationError,
    VideoFetchError,
)
from ytdlp_subs.domain.models import (
    ChannelUrl,
    DownloadProgress,
    SubtitleFile,
    SubtitleFormat,
    SubtitleLanguage,
    VideoId,
    VideoMetadata,
)

__all__ = [
    # Exceptions
    "SubtitleDownloaderError",
    "VideoFetchError",
    "SubtitleNotFoundError",
    "DownloadError",
    "FileProcessingError",
    "ConfigurationError",
    "CacheError",
    "ValidationError",
    "CommandExecutionError",
    # Models
    "VideoId",
    "ChannelUrl",
    "VideoMetadata",
    "SubtitleFile",
    "SubtitleFormat",
    "SubtitleLanguage",
    "DownloadProgress",
]
