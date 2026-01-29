"""Domain models for the subtitle downloader."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class SubtitleFormat(str, Enum):
    """Supported subtitle formats."""

    VTT = "vtt"
    SRT = "srt"
    TXT = "txt"


class SubtitleLanguage(str, Enum):
    """Common subtitle languages."""

    HINDI = "hi"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE = "zh"

    @classmethod
    def from_string(cls, lang: str) -> "SubtitleLanguage":
        """
        Create SubtitleLanguage from string.

        Args:
            lang: Language code string

        Returns:
            SubtitleLanguage enum value

        Raises:
            ValueError: If language code is not supported
        """
        try:
            return cls(lang.lower())
        except ValueError as e:
            raise ValueError(f"Unsupported language code: {lang}") from e


@dataclass(frozen=True)
class VideoId:
    """Value object representing a YouTube video ID."""

    value: str

    def __post_init__(self) -> None:
        """Validate video ID format."""
        if not self.value or len(self.value) != 11:
            raise ValueError(f"Invalid YouTube video ID: {self.value}")

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    @property
    def url(self) -> str:
        """Get full YouTube URL for this video."""
        return f"https://www.youtube.com/watch?v={self.value}"


@dataclass(frozen=True)
class ChannelUrl:
    """Value object representing a YouTube channel URL."""

    value: str

    def __post_init__(self) -> None:
        """Validate channel URL format."""
        if not self.value or "youtube.com" not in self.value:
            raise ValueError(f"Invalid YouTube channel URL: {self.value}")

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass
class VideoMetadata:
    """Entity representing video metadata."""

    video_id: VideoId
    title: str
    duration: Optional[int] = None
    upload_date: Optional[datetime] = None
    channel: Optional[str] = None
    description: Optional[str] = None
    view_count: Optional[int] = None
    available_subtitles: list[SubtitleLanguage] = field(default_factory=list)

    def has_subtitle(self, language: SubtitleLanguage) -> bool:
        """
        Check if subtitle is available in given language.

        Args:
            language: Language to check

        Returns:
            True if subtitle is available
        """
        return language in self.available_subtitles


@dataclass
class SubtitleFile:
    """Entity representing a downloaded subtitle file."""

    video_id: VideoId
    language: SubtitleLanguage
    format: SubtitleFormat
    file_path: Path
    size_bytes: int
    downloaded_at: datetime = field(default_factory=datetime.now)

    def exists(self) -> bool:
        """Check if file exists on disk."""
        return self.file_path.exists()

    def delete(self) -> None:
        """Delete the subtitle file."""
        if self.exists():
            self.file_path.unlink()


@dataclass
class DownloadProgress:
    """Value object representing download progress."""

    total_videos: int
    processed_videos: int
    skipped_videos: int
    failed_videos: int
    current_video: Optional[VideoId] = None

    @property
    def remaining_videos(self) -> int:
        """Calculate remaining videos to process."""
        return self.total_videos - self.processed_videos - self.skipped_videos

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.processed_videos == 0:
            return 0.0
        successful = self.processed_videos - self.failed_videos
        return (successful / self.processed_videos) * 100

    def __str__(self) -> str:
        """Return human-readable progress string."""
        return (
            f"Progress: {self.processed_videos}/{self.total_videos} "
            f"(Skipped: {self.skipped_videos}, Failed: {self.failed_videos}, "
            f"Success Rate: {self.success_rate:.1f}%)"
        )
