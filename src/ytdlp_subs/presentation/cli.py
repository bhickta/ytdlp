"""CLI presentation layer using Rich for beautiful output."""

import sys
from typing import NoReturn

import argparse
from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from ytdlp_subs import __version__
from ytdlp_subs.application.container import Container
from ytdlp_subs.domain.exceptions import SubtitleDownloaderError
from ytdlp_subs.domain.models import DownloadProgress
from ytdlp_subs.infrastructure.config import AppConfig
from ytdlp_subs.infrastructure.logging import configure_logging, get_logger

console = Console()
logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="ytdlp-subs",
        description="Download auto-subtitles from YouTube channels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download Hindi and English subtitles
  ytdlp-subs "https://www.youtube.com/@channel/videos" --lang hi,en

  # Save to specific directory with clean text output
  ytdlp-subs "URL" --output-dir ./subs --clean-txt

  # Use browser cookies to avoid rate limiting
  ytdlp-subs "URL" --cookies-from-browser chrome

  # Cache video list for faster reruns
  ytdlp-subs "URL" --cache-file ./cache.txt
        """,
    )

    parser.add_argument(
        "channel_url",
        help="YouTube channel URL (e.g., https://www.youtube.com/@channel/videos)",
    )

    parser.add_argument(
        "--lang",
        dest="language_preferences",
        default="hi,en",
        help="Comma-separated language preferences (default: hi,en)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("subtitles"),
        help="Directory to save subtitles (default: subtitles)",
    )

    parser.add_argument(
        "--min-wait",
        dest="min_wait_seconds",
        type=float,
        default=5.0,
        help="Minimum wait time between downloads in seconds (default: 5.0)",
    )

    parser.add_argument(
        "--max-wait",
        dest="max_wait_seconds",
        type=float,
        default=15.0,
        help="Maximum wait time between downloads in seconds (default: 15.0)",
    )

    parser.add_argument(
        "--cookies-from-browser",
        help="Browser to extract cookies from (e.g., chrome, firefox)",
    )

    parser.add_argument(
        "--cache-file",
        type=Path,
        help="Path to cache file for video IDs",
    )

    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh cache from network",
    )

    parser.add_argument(
        "--no-numbering",
        dest="enable_numbering",
        action="store_false",
        help="Disable prepending sequential numbers to filenames",
    )

    parser.add_argument(
        "--clean-txt",
        action="store_true",
        help="Convert VTT subtitles to clean TXT format",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        help="Path to log file (optional)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def display_progress_table(progress: DownloadProgress) -> None:
    """Display progress as a rich table."""
    table = Table(title="Download Progress", show_header=True, header_style="bold magenta")

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Total Videos", str(progress.total_videos))
    table.add_row("Processed", str(progress.processed_videos))
    table.add_row("Skipped", str(progress.skipped_videos))
    table.add_row("Failed", str(progress.failed_videos))
    table.add_row("Remaining", str(progress.remaining_videos))
    table.add_row("Success Rate", f"{progress.success_rate:.1f}%")

    if progress.current_video:
        table.add_row("Current Video", str(progress.current_video))

    console.print(table)


def run_download(config: AppConfig) -> int:
    """
    Run the download process.

    Args:
        config: Application configuration

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Create container and get orchestrator
        container = Container(config)
        orchestrator = container.download_orchestrator

        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress_bar:
            task = progress_bar.add_task(
                "[cyan]Downloading subtitles...",
                total=None,  # Will update when we know total
            )

            def progress_callback(prog: DownloadProgress) -> None:
                """Update progress bar."""
                if prog.total_videos > 0:
                    progress_bar.update(
                        task,
                        total=prog.total_videos,
                        completed=prog.processed_videos + prog.skipped_videos,
                        description=f"[cyan]Processing video {prog.processed_videos + prog.skipped_videos}/{prog.total_videos}",
                    )

            # Set progress callback
            orchestrator.progress_callback = progress_callback

            # Execute download
            final_progress = orchestrator.execute(
                channel_url=config.channel_url,
                output_dir=config.output_dir,
            )

        # Display final results
        console.print("\n[bold green]✓ Download completed![/bold green]\n")
        display_progress_table(final_progress)

        # Return error code if there were failures
        if final_progress.failed_videos > 0:
            console.print(
                f"\n[yellow]⚠ Warning: {final_progress.failed_videos} videos failed to download[/yellow]"
            )
            return 1

        return 0

    except SubtitleDownloaderError as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e.message}", style="red")
        logger.error("Download failed", error=str(e), context=e.context)
        return 1

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Download interrupted by user[/yellow]")
        logger.info("Download interrupted by user")
        return 1

    except Exception as e:
        console.print(f"\n[bold red]✗ Unexpected error:[/bold red] {e}", style="red")
        logger.exception("Unexpected error during download")
        return 1


def main() -> NoReturn:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Create configuration from CLI args
    try:
        config = AppConfig(
            channel_url=args.channel_url,
            language_preferences=args.language_preferences,
            output_dir=args.output_dir,
            min_wait_seconds=args.min_wait_seconds,
            max_wait_seconds=args.max_wait_seconds,
            cookies_from_browser=args.cookies_from_browser,
            cache_file=args.cache_file,
            force_refresh=args.force_refresh,
            enable_numbering=args.enable_numbering,
            clean_txt=args.clean_txt,
            log_level=args.log_level,
            log_file=args.log_file,
        )
    except Exception as e:
        console.print(f"[bold red]✗ Configuration error:[/bold red] {e}", style="red")
        sys.exit(1)

    # Configure logging
    configure_logging(
        log_level=config.log_level,
        log_file=config.log_file,
        json_logs=False,
    )

    # Display banner
    console.print(f"\n[bold cyan]YT-DLP Subtitle Downloader v{__version__}[/bold cyan]\n")

    # Run download
    exit_code = run_download(config)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
