# Quick Start

## Installation (30 seconds)

```bash
cd ytdlp
uv venv && source .venv/bin/activate
uv pip install -e .
```

## Basic Usage (1 command)

```bash
ytdlp-subs "https://www.youtube.com/@channel/videos"
```

## Your Exact Command

```bash
ytdlp-subs "URL" \
  --lang "hi,en" \
  --output-dir "." \
  --min-wait 1 \
  --max-wait 2 \
  --cookies-from-browser firefox \
  --cache-file "id_cache.txt" \
  --clean-txt
```

## What Changed from `sub-downloader`

**Only the command name:**
- Old: `sub-downloader`
- New: `ytdlp-subs`

Everything else works identically!

## Documentation

- [Getting Started](docs/getting-started.md) - Full installation guide
- [Usage Guide](docs/usage-guide.md) - All features explained
- [Migration Guide](docs/migration-guide.md) - Migrate from old version
- [Architecture](docs/architecture.md) - Design & patterns
- [API Reference](docs/api-reference.md) - Programmatic usage
- [Development](docs/development.md) - Contributing

## Key Features

✅ Multi-language support (hi, en, es, fr, de, ja, ko, zh)  
✅ Smart caching for resume capability  
✅ Rate limiting to avoid bans  
✅ Clean text conversion (VTT → TXT)  
✅ Beautiful progress bars  
✅ Browser cookie support  
✅ Type-safe with mypy  
✅ Production-ready error handling  

## Architecture Highlights

- **Clean Architecture** - Domain-driven design
- **SOLID Principles** - Maintainable & testable
- **Design Patterns** - Repository, Factory, Strategy
- **Type Safety** - Full type hints
- **DRY** - No code duplication
- **Single Responsibility** - Each class has one job

## Project Structure

```
src/ytdlp_subs/
├── domain/          # Business logic (framework-independent)
├── application/     # Use cases & orchestration
├── infrastructure/  # External concerns (I/O, APIs)
└── presentation/    # User interface (CLI)
```

## Development

```bash
# Install with dev tools
uv pip install -e ".[dev]"

# Run linting
ruff check src/

# Run type checking
mypy src/

# Run tests
pytest
```

## Help

```bash
ytdlp-subs --help
```

## Version

```bash
ytdlp-subs --version
```
