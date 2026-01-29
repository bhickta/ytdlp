# Architecture

## Overview

This project follows **Clean Architecture** (Hexagonal Architecture) with clear separation of concerns and dependency inversion.

## Layer Structure

```
┌─────────────────────────────────────────────┐
│         Presentation Layer (CLI)            │
│         - User Interface                    │
│         - Rich Console Output               │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Application Layer                   │
│         - Use Cases (Orchestrators)         │
│         - Service Implementations           │
│         - Dependency Injection              │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Domain Layer (Core)                 │
│         - Business Logic                    │
│         - Entities & Value Objects          │
│         - Repository Interfaces             │
│         - Service Interfaces                │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Infrastructure Layer                │
│         - Repository Implementations        │
│         - External APIs (yt-dlp)            │
│         - File System                       │
│         - Configuration                     │
└─────────────────────────────────────────────┘
```

## SOLID Principles

### Single Responsibility Principle (SRP)

Each class has one reason to change:

- `VideoId` - Represents video identifier
- `SubtitleDownloader` - Downloads subtitles
- `FilenameGenerator` - Generates filenames
- `CacheRepository` - Manages cache

### Open/Closed Principle (OCP)

Open for extension, closed for modification:

- New file processors can be added without modifying existing code
- New repository implementations can be swapped via interfaces
- New languages added via enum extension

### Liskov Substitution Principle (LSP)

Interfaces can be substituted:

```python
# Any IVideoRepository implementation works
video_repo: IVideoRepository = YtDlpVideoRepository(...)
# OR
video_repo: IVideoRepository = MockVideoRepository(...)
```

### Interface Segregation Principle (ISP)

Small, focused interfaces:

- `IVideoRepository` - Only video operations
- `ISubtitleRepository` - Only subtitle operations
- `ICacheRepository` - Only cache operations

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions:

```python
class DownloadOrchestrator:
    def __init__(
        self,
        video_repository: IVideoRepository,  # Interface, not concrete class
        subtitle_repository: ISubtitleRepository,
        # ...
    ):
```

## Design Patterns

### Repository Pattern

Abstracts data access:

```python
# Interface
class IVideoRepository(ABC):
    @abstractmethod
    def get_video_metadata(self, video_id: VideoId) -> VideoMetadata:
        pass

# Implementation
class YtDlpVideoRepository(IVideoRepository):
    def get_video_metadata(self, video_id: VideoId) -> VideoMetadata:
        # Actual yt-dlp logic
```

### Factory Pattern

Creates objects via Container:

```python
class Container:
    @property
    def video_repository(self) -> YtDlpVideoRepository:
        if self._video_repository is None:
            self._video_repository = YtDlpVideoRepository(
                command_executor=self.command_executor,
                cookies_from_browser=self.config.cookies_from_browser,
            )
        return self._video_repository
```

### Strategy Pattern

Pluggable file processors:

```python
class IFileProcessorService(ABC):
    @abstractmethod
    def process_file(self, input_file: Path) -> Path:
        pass

# Different strategies
class SubtitleFileProcessor(IFileProcessorService):
    # VTT to TXT conversion

class NoOpFileProcessor(IFileProcessorService):
    # No processing
```

### Value Object Pattern

Immutable domain primitives:

```python
@dataclass(frozen=True)
class VideoId:
    value: str
    
    def __post_init__(self) -> None:
        if len(self.value) != 11:
            raise ValueError("Invalid video ID")
```

### Use Case Pattern

Orchestrates business logic:

```python
class DownloadOrchestrator:
    def execute(self, channel_url: str) -> DownloadProgress:
        # Coordinates all services and repositories
```

## Dependency Flow

```
CLI → Container → Orchestrator → Services → Repositories → External APIs
 ↓                                   ↓           ↓
Config                           Domain      Domain
                                 Models    Interfaces
```

**Key principle:** Dependencies point inward toward domain layer.

## Component Responsibilities

### Domain Layer

**Models (`domain/models.py`):**
- `VideoId` - Value object for video identifier
- `VideoMetadata` - Entity for video information
- `SubtitleFile` - Entity for subtitle file
- `DownloadProgress` - Value object for progress tracking

**Exceptions (`domain/exceptions.py`):**
- Custom exception hierarchy
- Domain-specific error types

**Interfaces (`domain/repositories.py`, `domain/services.py`):**
- Contracts for repositories
- Contracts for services

### Application Layer

**Use Cases (`application/use_cases/`):**
- `DownloadOrchestrator` - Main business logic

**Services (`application/services/`):**
- `YtDlpSubtitleDownloader` - Downloads subtitles
- `SubtitleFileProcessor` - Processes files
- `FilenameGenerator` - Generates filenames

**Container (`application/container.py`):**
- Dependency injection
- Object lifecycle management

### Infrastructure Layer

**Repositories (`infrastructure/repositories/`):**
- `YtDlpVideoRepository` - Fetches video data
- `FileSystemSubtitleRepository` - Manages subtitle files
- `FileCacheRepository` - Manages cache

**Utilities:**
- `CommandExecutor` - Runs external commands
- `AppConfig` - Configuration management
- `Logging` - Structured logging

### Presentation Layer

**CLI (`presentation/cli.py`):**
- Argument parsing
- Progress display
- Error presentation

## Data Flow Example

**Download subtitle for a video:**

```
1. CLI receives user input
   ↓
2. Container creates dependencies
   ↓
3. DownloadOrchestrator.execute()
   ↓
4. VideoRepository.get_channel_video_ids()
   ↓
5. SubtitleRepository.get_downloaded_video_ids()
   ↓
6. For each video:
   a. SubtitleDownloader.download_subtitle()
   b. VideoRepository.get_video_metadata()
   c. FilenameGenerator.generate_filename()
   d. FileProcessor.process_file()
   e. SubtitleRepository.save_subtitle()
   ↓
7. Return DownloadProgress
   ↓
8. CLI displays results
```

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
def test_video_id_validation():
    # Valid ID
    vid = VideoId("dQw4w9WgXcQ")
    assert str(vid) == "dQw4w9WgXcQ"
    
    # Invalid ID
    with pytest.raises(ValueError):
        VideoId("invalid")
```

### Integration Tests

Test component interactions:

```python
def test_download_orchestrator(mock_repositories):
    orchestrator = DownloadOrchestrator(
        video_repository=mock_repositories.video,
        subtitle_repository=mock_repositories.subtitle,
        # ...
    )
    
    progress = orchestrator.execute("channel_url")
    assert progress.total_videos > 0
```

### Mocking

Use interfaces for easy mocking:

```python
class MockVideoRepository(IVideoRepository):
    def get_channel_video_ids(self, channel_url: str) -> list[VideoId]:
        return [VideoId("test123456")]
```

## Extension Points

### Add New Language

```python
# domain/models.py
class SubtitleLanguage(str, Enum):
    # ... existing languages
    PORTUGUESE = "pt"  # Add new language
```

### Add New File Processor

```python
# application/services/custom_processor.py
class CustomProcessor(IFileProcessorService):
    def process_file(self, input_file: Path) -> Path:
        # Custom processing logic
        return output_file
```

### Add New Repository

```python
# infrastructure/repositories/database_repository.py
class DatabaseSubtitleRepository(ISubtitleRepository):
    def save_subtitle(self, subtitle: SubtitleFile) -> None:
        # Save to database instead of file system
```

## Benefits of This Architecture

1. **Testability** - Easy to mock dependencies
2. **Maintainability** - Clear separation of concerns
3. **Flexibility** - Swap implementations easily
4. **Scalability** - Add features without breaking existing code
5. **Type Safety** - Full type hints with mypy
6. **Documentation** - Self-documenting via interfaces
