"""
YT-DLP Subtitle Downloader.

A production-grade CLI tool for downloading YouTube channel subtitles.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from ytdlp_subs.domain.models import SubtitleLanguage, VideoMetadata

__all__ = ["SubtitleLanguage", "VideoMetadata", "__version__"]
