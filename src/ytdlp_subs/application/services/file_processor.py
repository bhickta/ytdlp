"""File processor service for subtitle file transformations."""

import re
from pathlib import Path
from typing import Optional

from ytdlp_subs.domain.exceptions import FileProcessingError
from ytdlp_subs.domain.models import SubtitleFormat
from ytdlp_subs.domain.services import IFileProcessorService
from ytdlp_subs.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SubtitleFileProcessor(IFileProcessorService):
    """Service for processing subtitle files."""

    def process_file(
        self,
        input_file: Path,
        output_format: Optional[SubtitleFormat] = None,
    ) -> Path:
        """
        Process a subtitle file.

        Args:
            input_file: Input file path
            output_format: Desired output format

        Returns:
            Path to processed file

        Raises:
            FileProcessingError: If processing fails
        """
        logger.info("Processing file", input_file=str(input_file), output_format=output_format)

        if not input_file.exists():
            raise FileProcessingError(
                f"Input file does not exist: {input_file}",
                file_path=str(input_file),
            )

        # If output format is TXT and input is VTT, clean it
        if output_format == SubtitleFormat.TXT and input_file.suffix == ".vtt":
            return self.clean_vtt_to_txt(input_file)

        # Otherwise, return as-is
        return input_file

    def clean_vtt_to_txt(self, vtt_file: Path) -> Path:
        """
        Convert VTT file to clean text format.

        This removes:
        - WEBVTT headers
        - Timestamps
        - HTML tags
        - Duplicate consecutive lines

        Args:
            vtt_file: VTT file path

        Returns:
            Path to cleaned text file

        Raises:
            FileProcessingError: If conversion fails
        """
        logger.info("Converting VTT to clean TXT", vtt_file=str(vtt_file))

        if not vtt_file.exists():
            raise FileProcessingError(
                f"VTT file does not exist: {vtt_file}",
                file_path=str(vtt_file),
            )

        txt_file = vtt_file.with_suffix(".txt")

        try:
            cleaned_lines = self._clean_vtt_content(vtt_file)

            # Write cleaned content
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned_lines))

            # Delete original VTT file
            vtt_file.unlink()

            logger.info(
                "Successfully converted VTT to TXT",
                vtt_file=str(vtt_file),
                txt_file=str(txt_file),
                lines=len(cleaned_lines),
            )

            return txt_file

        except (IOError, OSError) as e:
            logger.error(
                "Failed to convert VTT to TXT",
                vtt_file=str(vtt_file),
                error=str(e),
            )
            raise FileProcessingError(
                f"Failed to convert VTT to TXT: {e}",
                file_path=str(vtt_file),
            ) from e

    def _clean_vtt_content(self, vtt_file: Path) -> list[str]:
        """
        Clean VTT file content.

        Args:
            vtt_file: VTT file path

        Returns:
            List of cleaned lines
        """
        cleaned_lines: list[str] = []
        last_line: Optional[str] = None

        with open(vtt_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Skip timestamp lines (contains -->)
                if "-->" in line:
                    continue

                # Skip numeric lines (cue identifiers)
                if line.isdigit():
                    continue

                # Skip WEBVTT headers
                if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                    continue

                # Remove HTML tags
                line = re.sub(r"<[^>]+>", "", line).strip()

                # Skip if line is empty after cleaning
                if not line:
                    continue

                # Skip duplicate consecutive lines
                if line == last_line:
                    continue

                cleaned_lines.append(line)
                last_line = line

        return cleaned_lines
