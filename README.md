# YT-DLP Subtitle Downloader

A production-grade CLI tool for downloading YouTube channel subtitles with enterprise-level architecture.

## 🌟 Features

- **Download subtitles from entire YouTube channels** - Automatically fetch all videos
- **Multi-language support** - Prioritize your preferred languages
- **Smart caching** - Resume interrupted downloads and cache video lists
- **Rate limiting** - Configurable delays to be respectful to servers
- **Clean text output** - Convert VTT to clean TXT format
- **Progress tracking** - Beautiful progress bars and statistics
- **Production-ready** - Comprehensive error handling and logging
- **Type-safe** - Full type hints with mypy validation
- **Well-tested** - Unit test structure included

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
src/ytdlp_subs/
├── domain/              # Business logic & entities (framework-independent)
│   ├── models.py        # Domain models (VideoId, SubtitleFile, etc.)
│   ├── exceptions.py    # Domain exceptions
│   ├── repositories.py  # Repository interfaces
│   └── services.py      # Service interfaces
├── application/         # Use cases & orchestration
│   ├── services/        # Service implementations
│   ├── use_cases/       # Business use cases
│   └── container.py     # Dependency injection
├── infrastructure/      # External concerns (I/O, APIs, etc.)
│   ├── repositories/    # Repository implementations
│   ├── config.py        # Configuration management
│   ├── logging.py       # Structured logging
│   └── command_executor.py  # External command execution
└── presentation/        # User interface
    └── cli.py           # Command-line interface
```

### Design Patterns Used

- **Repository Pattern** - Abstract data access
- **Dependency Injection** - Loose coupling via Container
- **Factory Pattern** - Object creation in Container
- **Strategy Pattern** - Pluggable file processors
- **Value Objects** - Immutable domain primitives (VideoId, ChannelUrl)
- **Use Case Pattern** - Business logic orchestration

### SOLID Principles

- ✅ **Single Responsibility** - Each class has one reason to change
- ✅ **Open/Closed** - Open for extension, closed for modification
- ✅ **Liskov Substitution** - Interfaces can be swapped
- ✅ **Interface Segregation** - Small, focused interfaces
- ✅ **Dependency Inversion** - Depend on abstractions, not concretions

## 📦 Installation

### Using UV (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
cd ytdlp
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

### Using pip

```bash
cd ytdlp
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 🚀 Usage

### Basic Usage

```bash
# Download Hindi and English subtitles from a channel
ytdlp-subs "https://www.youtube.com/@channel/videos"
```

### Advanced Usage

```bash
# Custom languages and output directory
ytdlp-subs "https://www.youtube.com/@channel/videos" \
  --lang hi,en,es \
  --output-dir ./my-subtitles

# Convert to clean text format
ytdlp-subs "URL" --clean-txt

# Use browser cookies to avoid rate limiting
ytdlp-subs "URL" --cookies-from-browser chrome

# Cache video list for faster reruns
ytdlp-subs "URL" --cache-file ./cache.txt

# Adjust rate limiting
ytdlp-subs "URL" --min-wait 3 --max-wait 10

# Disable sequential numbering
ytdlp-subs "URL" --no-numbering

# Enable debug logging
ytdlp-subs "URL" --log-level DEBUG --log-file ./download.log
```

### All Options

```
positional arguments:
  channel_url           YouTube channel URL

options:
  --lang LANGUAGES      Comma-separated language preferences (default: hi,en)
  --output-dir DIR      Directory to save subtitles (default: subtitles)
  --min-wait SECONDS    Minimum wait between downloads (default: 5.0)
  --max-wait SECONDS    Maximum wait between downloads (default: 15.0)
  --cookies-from-browser BROWSER
                        Browser to extract cookies from (chrome, firefox, etc.)
  --cache-file PATH     Path to cache file for video IDs
  --force-refresh       Force refresh cache from network
  --no-numbering        Disable sequential numbering in filenames
  --clean-txt           Convert VTT to clean TXT format
  --log-level LEVEL     Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --log-file PATH       Path to log file
  --version             Show version and exit
```

## 🛠️ Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run linting
ruff check src/

# Run formatting
black src/
isort src/

# Run type checking
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=ytdlp_subs --cov-report=html
```

### Code Quality Tools

- **ruff** - Fast Python linter
- **black** - Code formatter
- **isort** - Import sorter
- **mypy** - Static type checker
- **pytest** - Testing framework

### Project Structure Explanation

#### Domain Layer (`domain/`)
Contains pure business logic with no external dependencies:
- **models.py** - Domain entities and value objects
- **exceptions.py** - Domain-specific exceptions
- **repositories.py** - Repository interfaces (contracts)
- **services.py** - Service interfaces (contracts)

#### Application Layer (`application/`)
Orchestrates domain logic and use cases:
- **services/** - Concrete service implementations
- **use_cases/** - Business use case orchestrators
- **container.py** - Dependency injection container

#### Infrastructure Layer (`infrastructure/`)
Handles external concerns:
- **repositories/** - Concrete repository implementations
- **config.py** - Configuration management (Pydantic)
- **logging.py** - Structured logging (structlog)
- **command_executor.py** - External command execution

#### Presentation Layer (`presentation/`)
User interface:
- **cli.py** - Command-line interface (Rich library)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ytdlp_subs --cov-report=term-missing

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

## 📝 Configuration

### Environment Variables

You can use environment variables prefixed with `YTDLP_SUBS_`:

```bash
export YTDLP_SUBS_CHANNEL_URL="https://youtube.com/@channel/videos"
export YTDLP_SUBS_LANGUAGE_PREFERENCES="hi,en"
export YTDLP_SUBS_OUTPUT_DIR="./subtitles"
export YTDLP_SUBS_MIN_WAIT_SECONDS=5.0
export YTDLP_SUBS_MAX_WAIT_SECONDS=15.0
```

### .env File

Create a `.env` file in your project root:

```env
YTDLP_SUBS_CHANNEL_URL=https://youtube.com/@channel/videos
YTDLP_SUBS_LANGUAGE_PREFERENCES=hi,en
YTDLP_SUBS_OUTPUT_DIR=./subtitles
YTDLP_SUBS_LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- CLI powered by [Rich](https://github.com/Textualize/rich)
- Configuration with [Pydantic](https://github.com/pydantic/pydantic)
- Logging with [structlog](https://github.com/hynek/structlog)

## 📚 Additional Resources

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)