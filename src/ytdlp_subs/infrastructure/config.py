"""Application configuration using Pydantic settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ytdlp_subs.domain.models import SubtitleLanguage


class AppConfig(BaseSettings):
    """Application configuration with validation."""

    model_config = SettingsConfigDict(
        env_prefix="YTDLP_SUBS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Channel settings
    channel_url: str = Field(..., description="YouTube channel URL")

    # Language preferences
    language_preferences: list[str] = Field(
        default=["hi", "en"],
        description="Comma-separated language preferences",
    )

    # Output settings
    output_dir: Path = Field(
        default=Path("subtitles"),
        description="Directory to save subtitles",
    )

    # Rate limiting
    min_wait_seconds: float = Field(
        default=5.0,
        ge=0.0,
        description="Minimum wait time between downloads",
    )
    max_wait_seconds: float = Field(
        default=15.0,
        ge=0.0,
        description="Maximum wait time between downloads",
    )

    # Browser cookies
    cookies_from_browser: Optional[str] = Field(
        default=None,
        description="Browser to extract cookies from (e.g., 'chrome', 'firefox')",
    )

    # Cache settings
    cache_file: Optional[Path] = Field(
        default=None,
        description="Path to cache file for video IDs",
    )
    force_refresh: bool = Field(
        default=False,
        description="Force refresh cache from network",
    )

    # File naming
    enable_numbering: bool = Field(
        default=True,
        description="Prepend sequential numbers to filenames",
    )

    # Processing options
    clean_txt: bool = Field(
        default=False,
        description="Convert VTT to clean TXT format",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_file: Optional[Path] = Field(
        default=None,
        description="Path to log file",
    )

    @field_validator("max_wait_seconds")
    @classmethod
    def validate_wait_times(cls, v: float, info) -> float:
        """Validate that max_wait is greater than min_wait."""
        min_wait = info.data.get("min_wait_seconds", 0.0)
        if v < min_wait:
            raise ValueError("max_wait_seconds must be >= min_wait_seconds")
        return v

    @field_validator("language_preferences", mode="before")
    @classmethod
    def parse_languages(cls, v: str | list[str]) -> list[str]:
        """Parse comma-separated language string."""
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",") if lang.strip()]
        return v

    @field_validator("output_dir", "cache_file", "log_file", mode="before")
    @classmethod
    def parse_path(cls, v: str | Path | None) -> Path | None:
        """Convert string to Path."""
        if v is None:
            return None
        return Path(v) if isinstance(v, str) else v

    def get_languages(self) -> list[SubtitleLanguage]:
        """
        Get validated subtitle languages.

        Returns:
            List of SubtitleLanguage enums

        Raises:
            ValueError: If any language code is invalid
        """
        return [SubtitleLanguage.from_string(lang) for lang in self.language_preferences]

    def ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self) -> Optional[Path]:
        """
        Get cache file path, creating parent directories if needed.

        Returns:
            Cache file path or None
        """
        if self.cache_file:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            return self.cache_file
        return None
