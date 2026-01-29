"""YT-DLP based video repository implementation."""

import json
from datetime import datetime
from typing import Optional

from ytdlp_subs.domain.exceptions import VideoFetchError
from ytdlp_subs.domain.models import SubtitleLanguage, VideoId, VideoMetadata
from ytdlp_subs.domain.repositories import IVideoRepository
from ytdlp_subs.infrastructure.command_executor import CommandExecutor
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class YtDlpVideoRepository(IVideoRepository):
    """YT-DLP based implementation of video repository."""

    def __init__(
        self,
        command_executor: CommandExecutor,
        cookies_from_browser: Optional[str] = None,
    ) -> None:
        """
        Initialize YT-DLP video repository.

        Args:
            command_executor: Command executor for running yt-dlp
            cookies_from_browser: Optional browser to extract cookies from
        """
        self.command_executor = command_executor
        self.cookies_from_browser = cookies_from_browser

    def get_video_metadata(self, video_id: VideoId) -> Optional[VideoMetadata]:
        """
        Retrieve video metadata using yt-dlp.

        Args:
            video_id: Video identifier

        Returns:
            VideoMetadata if successful

        Raises:
            VideoFetchError: If metadata fetch fails
        """
        logger.info("Fetching video metadata", video_id=str(video_id))

        command = self._build_metadata_command(video_id.url)

        try:
            result = self.command_executor.execute(command, check=True)

            # Parse JSON output (last line of stdout)
            json_output = result.stdout.strip().split("\n")[-1]
            data = json.loads(json_output)

            metadata = self._parse_metadata(data, video_id)

            logger.info(
                "Successfully fetched video metadata",
                video_id=str(video_id),
                title=metadata.title,
                available_subtitles=len(metadata.available_subtitles),
            )

            return metadata

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse video metadata JSON",
                video_id=str(video_id),
                error=str(e),
            )
            raise VideoFetchError(
                f"Failed to parse metadata for video {video_id}",
                video_id=str(video_id),
            ) from e

        except Exception as e:
            logger.error(
                "Failed to fetch video metadata",
                video_id=str(video_id),
                error=str(e),
            )
            raise VideoFetchError(
                f"Failed to fetch metadata for video {video_id}: {e}",
                video_id=str(video_id),
            ) from e

    def get_channel_video_ids(self, channel_url: str) -> list[VideoId]:
        """
        Retrieve all video IDs from a channel using yt-dlp.

        Args:
            channel_url: YouTube channel URL

        Returns:
            List of video IDs

        Raises:
            VideoFetchError: If channel fetch fails
        """
        logger.info("Fetching channel video IDs", channel_url=channel_url)

        command = self._build_channel_command(channel_url)

        try:
            result = self.command_executor.execute(command, check=True)

            # Each line is a video ID
            video_id_strings = [
                line.strip() for line in result.stdout.strip().split("\n") if line.strip()
            ]

            if not video_id_strings:
                logger.warning("No videos found in channel", channel_url=channel_url)
                return []

            video_ids = [VideoId(vid) for vid in video_id_strings]

            logger.info(
                "Successfully fetched channel video IDs",
                channel_url=channel_url,
                count=len(video_ids),
            )

            return video_ids

        except ValueError as e:
            logger.error(
                "Invalid video ID in channel",
                channel_url=channel_url,
                error=str(e),
            )
            raise VideoFetchError(
                f"Invalid video ID in channel: {e}",
                channel_url=channel_url,
            ) from e

        except Exception as e:
            logger.error(
                "Failed to fetch channel videos",
                channel_url=channel_url,
                error=str(e),
            )
            raise VideoFetchError(
                f"Failed to fetch channel videos: {e}",
                channel_url=channel_url,
            ) from e

    def _build_metadata_command(self, video_url: str) -> list[str]:
        """Build yt-dlp command for fetching metadata."""
        command = [
            "yt-dlp",
            "--dump-json",
            "--skip-download",
        ]

        if self.cookies_from_browser:
            command.extend(["--cookies-from-browser", self.cookies_from_browser])

        command.append(video_url)
        return command

    def _build_channel_command(self, channel_url: str) -> list[str]:
        """Build yt-dlp command for fetching channel videos."""
        command = [
            "yt-dlp",
            "--flat-playlist",
            "--print",
            "id",
        ]

        if self.cookies_from_browser:
            command.extend(["--cookies-from-browser", self.cookies_from_browser])

        command.append(channel_url)
        return command

    def _parse_metadata(self, data: dict, video_id: VideoId) -> VideoMetadata:
        """Parse yt-dlp JSON output into VideoMetadata."""
        # Parse available subtitles
        available_subs: list[SubtitleLanguage] = []
        automatic_captions = data.get("automatic_captions", {})

        for lang_code in automatic_captions.keys():
            try:
                lang = SubtitleLanguage.from_string(lang_code)
                available_subs.append(lang)
            except ValueError:
                # Skip unsupported languages
                logger.debug("Skipping unsupported language", language=lang_code)
                continue

        # Parse upload date
        upload_date = None
        if "upload_date" in data:
            try:
                upload_date = datetime.strptime(data["upload_date"], "%Y%m%d")
            except ValueError:
                logger.warning("Failed to parse upload date", date=data["upload_date"])

        return VideoMetadata(
            video_id=video_id,
            title=data.get("title", "Unknown Title"),
            duration=data.get("duration"),
            upload_date=upload_date,
            channel=data.get("channel"),
            description=data.get("description"),
            view_count=data.get("view_count"),
            available_subtitles=available_subs,
        )
