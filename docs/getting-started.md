# Getting Started

## Prerequisites

- Python 3.11 or higher
- `yt-dlp` installed and accessible in PATH
- Internet connection

## Installation

### Method 1: Using UV (Recommended)

UV is a fast Python package installer and resolver.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <repository-url>
cd ytdlp

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Install package
uv pip install -e .

# Verify installation
ytdlp-subs --version
```

### Method 2: Using pip

```bash
# Clone repository
git clone <repository-url>
cd ytdlp

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Install package
pip install -e .

# Verify installation
ytdlp-subs --version
```

### Installing yt-dlp

If you don't have `yt-dlp` installed:

```bash
# Using pip
pip install yt-dlp

# Using uv
uv pip install yt-dlp

# Verify installation
yt-dlp --version
```

## First Run

### Basic Example

Download Hindi and English subtitles from a channel:

```bash
ytdlp-subs "https://www.youtube.com/@channelname/videos"
```

This will:
1. Fetch all video IDs from the channel
2. Download subtitles in Hindi (preferred) or English (fallback)
3. Save files to `./subtitles/` directory
4. Show progress with a beautiful progress bar

### Output

```
YT-DLP Subtitle Downloader v1.0.0

Downloading subtitles... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:05:23

✓ Download completed!

┏━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric        ┃ Value ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Videos  │ 150   │
│ Processed     │ 145   │
│ Skipped       │ 0     │
│ Failed        │ 5     │
│ Remaining     │ 0     │
│ Success Rate  │ 96.7% │
└───────────────┴───────┘
```

## Common Use Cases

### Use Case 1: Educational Channel

Download all lectures from an educational channel:

```bash
ytdlp-subs "https://www.youtube.com/@educhannel/videos" \
  --output-dir ./lectures \
  --clean-txt
```

### Use Case 2: Multi-language Content

Download subtitles with Spanish priority:

```bash
ytdlp-subs "https://www.youtube.com/@channel/videos" \
  --lang es,en,hi
```

### Use Case 3: Large Channel with Caching

For channels with many videos, use caching:

```bash
# First run - fetches and caches video list
ytdlp-subs "https://www.youtube.com/@largechannel/videos" \
  --cache-file ./cache.txt

# Subsequent runs - uses cached list (much faster)
ytdlp-subs "https://www.youtube.com/@largechannel/videos" \
  --cache-file ./cache.txt

# Force refresh cache
ytdlp-subs "https://www.youtube.com/@largechannel/videos" \
  --cache-file ./cache.txt \
  --force-refresh
```

## Next Steps

- Read [Usage Guide](usage-guide.md) for advanced examples
- Explore [Architecture](architecture.md) to understand the design
- Check [Development](development.md) to contribute
