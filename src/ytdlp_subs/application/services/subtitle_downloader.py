"""Subtitle downloader service implementation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ytdlp_subs.domain.exceptions import DownloadError, SubtitleNotFoundError
from ytdlp_subs.domain.models import SubtitleFile, SubtitleFormat, SubtitleLanguage, VideoId
from ytdlp_subs.domain.services import ISubtitleDownloaderService
from ytdlp_subs.infrastructure.command_executor import CommandExecutor
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class YtDlpSubtitleDownloader(ISubtitleDownloaderService):
    """YT-DLP based subtitle downloader service."""

    def __init__(
        self,
        command_executor: CommandExecutor,
        cookies_from_browser: Optional[str] = None,
    ) -> None:
        """
        Initialize subtitle downloader.

        Args:
            command_executor: Command executor for running yt-dlp
            cookies_from_browser: Optional browser to extract cookies from
        """
        self.command_executor = command_executor
        self.cookies_from_browser = cookies_from_browser

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
            SubtitleFile if successful, None if subtitle not available

        Raises:
            DownloadError: If download fails
        """
        logger.info(
            "Downloading subtitle",
            video_id=str(video_id),
            language=language.value,
        )

        # Create temporary template for download
        temp_template = output_dir / f"{video_id}_{language.value}.temp"

        command = self._build_download_command(
            video_id.url,
            language.value,
            str(temp_template),
        )

        try:
            result = self.command_executor.execute(command, check=True)

            # Parse JSON output to get subtitle info
            json_output = result.stdout.strip().split("\n")[-1]
            metadata = json.loads(json_output)

            # Check if subtitle was actually downloaded
            requested_subs = metadata.get("requested_subtitles")

            # Handle case where requested_subtitles is None or language not available
            if not requested_subs or language.value not in requested_subs:
                logger.info(
                    "Subtitle not available",
                    video_id=str(video_id),
                    language=language.value,
                )
                return None

            # Find the downloaded file
            subtitle_info = requested_subs[language.value]
            ext = subtitle_info.get("ext", "vtt")
            temp_file = output_dir / f"{video_id}_{language.value}.temp.{language.value}.{ext}"

            if not temp_file.exists():
                logger.error(
                    "Downloaded subtitle file not found",
                    video_id=str(video_id),
                    expected_path=str(temp_file),
                )
                raise DownloadError(
                    f"Downloaded subtitle file not found: {temp_file}",
                    video_id=str(video_id),
                    language=language.value,
                )

            # Create SubtitleFile object
            subtitle_file = SubtitleFile(
                video_id=video_id,
                language=language,
                format=SubtitleFormat(ext),
                file_path=temp_file,
                size_bytes=temp_file.stat().st_size,
                downloaded_at=datetime.now(),
            )

            logger.info(
                "Successfully downloaded subtitle",
                video_id=str(video_id),
                language=language.value,
                file_path=str(temp_file),
                size_bytes=subtitle_file.size_bytes,
            )

            return subtitle_file

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse download output",
                video_id=str(video_id),
                error=str(e),
            )
            raise DownloadError(
                f"Failed to parse download output for {video_id}",
                video_id=str(video_id),
            ) from e

        except Exception as e:
            logger.error(
                "Failed to download subtitle",
                video_id=str(video_id),
                language=language.value,
                error=str(e),
            )
            raise DownloadError(
                f"Failed to download subtitle: {e}",
                video_id=str(video_id),
                language=language.value,
            ) from e

    def _build_download_command(
        self,
        video_url: str,
        language: str,
        temp_template: str,
    ) -> list[str]:
        """Build yt-dlp command for downloading subtitle."""
        command = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang",
            language,
            "--skip-download",
            "--output",
            temp_template,
            "--print-json",
        ]

        if self.cookies_from_browser:
            command.extend(["--cookies-from-browser", self.cookies_from_browser])

        command.append(video_url)
        return command
