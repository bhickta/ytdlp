# API Reference

Quick reference for programmatic usage.

## CLI Entry Point

```python
from ytdlp_subs.presentation.cli import main

# Run CLI programmatically
main()
```

## Domain Models

### VideoId

```python
from ytdlp_subs.domain.models import VideoId

# Create video ID
video_id = VideoId("dQw4w9WgXcQ")

# Get URL
url = video_id.url  # "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# String representation
str(video_id)  # "dQw4w9WgXcQ"
```

### SubtitleLanguage

```python
from ytdlp_subs.domain.models import SubtitleLanguage

# Use enum
lang = SubtitleLanguage.HINDI  # "hi"
lang = SubtitleLanguage.ENGLISH  # "en"

# From string
lang = SubtitleLanguage.from_string("hi")
```

### VideoMetadata

```python
from ytdlp_subs.domain.models import VideoMetadata, VideoId

metadata = VideoMetadata(
    video_id=VideoId("dQw4w9WgXcQ"),
    title="Video Title",
    duration=180,
    channel="Channel Name",
)

# Check subtitle availability
has_hindi = metadata.has_subtitle(SubtitleLanguage.HINDI)
```

## Configuration

### AppConfig

```python
from ytdlp_subs.infrastructure.config import AppConfig
from pathlib import Path

# Create configuration
config = AppConfig(
    channel_url="https://www.youtube.com/@channel/videos",
    language_preferences=["hi", "en"],
    output_dir=Path("./subtitles"),
    min_wait_seconds=5.0,
    max_wait_seconds=15.0,
    clean_txt=True,
)

# Get validated languages
languages = config.get_languages()  # [SubtitleLanguage.HINDI, SubtitleLanguage.ENGLISH]

# Ensure output directory exists
config.ensure_output_dir()
```

## Dependency Injection

### Container

```python
from ytdlp_subs.application.container import Container
from ytdlp_subs.infrastructure.config import AppConfig

# Create config
config = AppConfig(channel_url="URL", ...)

# Create container
container = Container(config)

# Get orchestrator
orchestrator = container.download_orchestrator

# Execute download
progress = orchestrator.execute(
    channel_url=config.channel_url,
    output_dir=config.output_dir,
)
```

## Use Cases

### DownloadOrchestrator

```python
from ytdlp_subs.application.use_cases.download_orchestrator import DownloadOrchestrator
from ytdlp_subs.domain.models import DownloadProgress

def progress_callback(progress: DownloadProgress) -> None:
    print(f"Processed: {progress.processed_videos}/{progress.total_videos}")

# Create orchestrator (via container)
orchestrator = container.download_orchestrator
orchestrator.progress_callback = progress_callback

# Execute
final_progress = orchestrator.execute(
    channel_url="https://www.youtube.com/@channel/videos",
    output_dir=Path("./subtitles"),
)

# Check results
print(f"Success rate: {final_progress.success_rate:.1f}%")
```

## Services

### SubtitleDownloader

```python
from ytdlp_subs.application.services.subtitle_downloader import YtDlpSubtitleDownloader
from ytdlp_subs.infrastructure.command_executor import CommandExecutor

executor = CommandExecutor()
downloader = YtDlpSubtitleDownloader(
    command_executor=executor,
    cookies_from_browser="firefox",
)

# Download subtitle
subtitle_file = downloader.download_subtitle(
    video_id=VideoId("dQw4w9WgXcQ"),
    language=SubtitleLanguage.HINDI,
    output_dir=Path("./subs"),
)

if subtitle_file:
    print(f"Downloaded: {subtitle_file.file_path}")
```

### FileProcessor

```python
from ytdlp_subs.application.services.file_processor import SubtitleFileProcessor
from ytdlp_subs.domain.models import SubtitleFormat

processor = SubtitleFileProcessor()

# Convert VTT to TXT
txt_file = processor.clean_vtt_to_txt(Path("subtitle.vtt"))

# Process with format
output = processor.process_file(
    input_file=Path("subtitle.vtt"),
    output_format=SubtitleFormat.TXT,
)
```

### FilenameGenerator

```python
from ytdlp_subs.application.services.filename_generator import FilenameGenerator

generator = FilenameGenerator(enable_numbering=True)

filename = generator.generate_filename(
    video_metadata=metadata,
    language=SubtitleLanguage.HINDI,
    format=SubtitleFormat.VTT,
    index=1,
    total_count=100,
)
# "001_dQw4w9WgXcQ_Video_Title.hi.vtt"
```

## Repositories

### VideoRepository

```python
from ytdlp_subs.infrastructure.repositories import YtDlpVideoRepository

video_repo = YtDlpVideoRepository(
    command_executor=executor,
    cookies_from_browser="firefox",
)

# Get channel videos
video_ids = video_repo.get_channel_video_ids(
    "https://www.youtube.com/@channel/videos"
)

# Get video metadata
metadata = video_repo.get_video_metadata(VideoId("dQw4w9WgXcQ"))
```

### SubtitleRepository

```python
from ytdlp_subs.infrastructure.repositories import FileSystemSubtitleRepository

subtitle_repo = FileSystemSubtitleRepository(output_dir=Path("./subs"))

# Check if subtitle exists
exists = subtitle_repo.subtitle_exists(VideoId("dQw4w9WgXcQ"))

# Get downloaded video IDs
downloaded = subtitle_repo.get_downloaded_video_ids()
```

### CacheRepository

```python
from ytdlp_subs.infrastructure.repositories import FileCacheRepository

cache_repo = FileCacheRepository(cache_file=Path("cache.txt"))

# Get cached video IDs
cached_ids = cache_repo.get_cached_video_ids()

# Save video IDs
cache_repo.save_video_ids([VideoId("id1"), VideoId("id2")])

# Clear cache
cache_repo.clear_cache()
```

## Logging

### Configure Logging

```python
from ytdlp_subs.infrastructure.logging import configure_logging, get_logger

# Configure
configure_logging(
    log_level="DEBUG",
    log_file=Path("app.log"),
    json_logs=False,
)

# Get logger
logger = get_logger(__name__)

# Log messages
logger.info("Processing video", video_id="dQw4w9WgXcQ")
logger.error("Download failed", error="Connection timeout")
```

## Exceptions

### Exception Hierarchy

```python
from ytdlp_subs.domain.exceptions import (
    SubtitleDownloaderError,  # Base exception
    VideoFetchError,
    SubtitleNotFoundError,
    DownloadError,
    FileProcessingError,
    ConfigurationError,
    CacheError,
)

try:
    # Download subtitle
    subtitle = downloader.download_subtitle(...)
except SubtitleNotFoundError as e:
    print(f"Subtitle not available: {e.message}")
    print(f"Context: {e.context}")
except DownloadError as e:
    print(f"Download failed: {e.message}")
except SubtitleDownloaderError as e:
    print(f"General error: {e.message}")
```

## Complete Example

```python
from pathlib import Path
from ytdlp_subs.infrastructure.config import AppConfig
from ytdlp_subs.application.container import Container
from ytdlp_subs.infrastructure.logging import configure_logging
from ytdlp_subs.domain.models import DownloadProgress

# Configure logging
configure_logging(log_level="INFO")

# Create configuration
config = AppConfig(
    channel_url="https://www.youtube.com/@channel/videos",
    language_preferences=["hi", "en"],
    output_dir=Path("./subtitles"),
    min_wait_seconds=5.0,
    max_wait_seconds=15.0,
    clean_txt=True,
    cache_file=Path("cache.txt"),
)

# Create container
container = Container(config)

# Get orchestrator
orchestrator = container.download_orchestrator

# Add progress callback
def on_progress(progress: DownloadProgress) -> None:
    print(f"Progress: {progress.processed_videos}/{progress.total_videos}")

orchestrator.progress_callback = on_progress

# Execute download
try:
    final_progress = orchestrator.execute(
        channel_url=config.channel_url,
        output_dir=config.output_dir,
    )
    
    print(f"Completed! Success rate: {final_progress.success_rate:.1f}%")
    
except Exception as e:
    print(f"Error: {e}")
```

## Type Hints

All code is fully typed. Use mypy for type checking:

```bash
mypy src/ytdlp_subs/
```

## Testing

### Mock Repositories

```python
from ytdlp_subs.domain.repositories import IVideoRepository
from ytdlp_subs.domain.models import VideoId

class MockVideoRepository(IVideoRepository):
    def get_channel_video_ids(self, channel_url: str) -> list[VideoId]:
        return [VideoId("test123456")]
    
    def get_video_metadata(self, video_id: VideoId):
        return VideoMetadata(video_id=video_id, title="Test Video")

# Use in tests
mock_repo = MockVideoRepository()
orchestrator = DownloadOrchestrator(video_repository=mock_repo, ...)
```
