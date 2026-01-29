# Documentation Index

## Quick Links

- [Getting Started](getting-started.md) - Installation and first steps
- [Usage Guide](usage-guide.md) - Detailed usage examples
- [Migration Guide](migration-guide.md) - Migrate from old `sub-downloader`
- [Architecture](architecture.md) - System design and patterns
- [API Reference](api-reference.md) - Code documentation
- [Development](development.md) - Contributing guide

## Overview

YT-DLP Subtitle Downloader is a production-grade CLI tool for downloading YouTube channel subtitles with enterprise-level architecture following Clean Architecture and SOLID principles.

## Key Features

- **Multi-language support** with priority ordering
- **Smart caching** for resume capability
- **Rate limiting** to respect server resources
- **Clean text conversion** from VTT format
- **Progress tracking** with beautiful UI
- **Type-safe** with full mypy validation
- **Production-ready** error handling

## Quick Start

```bash
# Install with uv
uv pip install -e .

# Download subtitles
ytdlp-subs "https://www.youtube.com/@channel/videos"
```

See [Getting Started](getting-started.md) for detailed installation instructions.
