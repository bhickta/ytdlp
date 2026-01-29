# Migration Guide

## Migrating from `sub-downloader` to `ytdlp-subs`

This guide helps you migrate from the old `sub-downloader` CLI to the new `ytdlp-subs` architecture.

## Quick Reference

### Command Name Change

**Old:** `sub-downloader`  
**New:** `ytdlp-subs`

### Arguments (Unchanged)

All arguments work exactly the same way:

| Old Argument | New Argument | Status |
|--------------|--------------|--------|
| `--lang` | `--lang` | ✅ Same |
| `--output-dir` | `--output-dir` | ✅ Same |
| `--min-wait` | `--min-wait` | ✅ Same (now `--min-wait` instead of `--min-wait`) |
| `--max-wait` | `--max-wait` | ✅ Same (now `--max-wait` instead of `--max-wait`) |
| `--cookies-from-browser` | `--cookies-from-browser` | ✅ Same |
| `--cache-file` | `--cache-file` | ✅ Same |
| `--force-refresh` | `--force-refresh` | ✅ Same |
| `--no-numbering` | `--no-numbering` | ✅ Same |
| `--clean-txt` | `--clean-txt` | ✅ Same |

## Your Exact Command

### Old Command
```bash
sub-downloader "https://youtu.be/OXh5ok4GU-4?list=PLg5vXp1Sasokg-1VUqYZhoIgpPZ1dDD8y" \
  --lang "hi,en" \
  --output-dir "." \
  --min-wait 1 \
  --max-wait 2 \
  --cookies-from-browser firefox \
  --cache-file "id_cache.txt" \
  --clean-txt
```

### New Command
```bash
ytdlp-subs "https://youtu.be/OXh5ok4GU-4?list=PLg5vXp1Sasokg-1VUqYZhoIgpPZ1dDD8y" \
  --lang "hi,en" \
  --output-dir "." \
  --min-wait 1 \
  --max-wait 2 \
  --cookies-from-browser firefox \
  --cache-file "id_cache.txt" \
  --clean-txt
```

**What changed:** Only the command name (`sub-downloader` → `ytdlp-subs`)

## Installation

### Uninstall Old Version

```bash
# If installed with pip
pip uninstall sub_downloader

# Remove old files
rm -rf src/sub_downloader
rm -rf src/sub_downloader.egg-info
```

### Install New Version

```bash
# With uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .

# Verify
ytdlp-subs --version
```

## Shell Alias (Optional)

If you want to keep using `sub-downloader`:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias sub-downloader='ytdlp-subs'

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

Now your old command works unchanged:
```bash
sub-downloader "URL" --lang "hi,en" --clean-txt
```

## What's New

### 1. Better Architecture

- **Clean Architecture** with SOLID principles
- **Type-safe** with full mypy validation
- **Testable** with dependency injection
- **Maintainable** with clear separation of concerns

### 2. Improved Error Handling

```python
# Old: Generic exceptions
Exception: Command failed

# New: Specific exceptions
DownloadError: Failed to download subtitle for video dQw4w9WgXcQ
  Context: {"video_id": "dQw4w9WgXcQ", "language": "hi"}
```

### 3. Structured Logging

```bash
# Enable structured logging
ytdlp-subs "URL" --log-file download.log --log-level DEBUG
```

**Log output:**
```json
{"timestamp": "2026-01-29T18:30:00", "level": "INFO", "event": "Downloading subtitle", "video_id": "dQw4w9WgXcQ"}
```

### 4. Better Progress Display

Old:
```
Processing Video 1 of 100 (Global Index: 1)
  Waiting for 7.23 seconds...
```

New:
```
YT-DLP Subtitle Downloader v1.0.0

Downloading subtitles... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:05:23

✓ Download completed!

┏━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric        ┃ Value ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Videos  │ 100   │
│ Processed     │ 95    │
│ Skipped       │ 0     │
│ Failed        │ 5     │
│ Success Rate  │ 95.0% │
└───────────────┴───────┘
```

### 5. Environment Variables

New feature - set defaults via environment:

```bash
export YTDLP_SUBS_LANGUAGE_PREFERENCES="hi,en"
export YTDLP_SUBS_OUTPUT_DIR="./subtitles"
export YTDLP_SUBS_MIN_WAIT_SECONDS=1.0
export YTDLP_SUBS_MAX_WAIT_SECONDS=2.0
export YTDLP_SUBS_COOKIES_FROM_BROWSER="firefox"

# Now just run with URL
ytdlp-subs "URL"
```

### 6. Configuration File

New feature - use `.env` file:

```bash
# .env
YTDLP_SUBS_LANGUAGE_PREFERENCES=hi,en
YTDLP_SUBS_OUTPUT_DIR=.
YTDLP_SUBS_MIN_WAIT_SECONDS=1.0
YTDLP_SUBS_MAX_WAIT_SECONDS=2.0
YTDLP_SUBS_COOKIES_FROM_BROWSER=firefox
YTDLP_SUBS_CLEAN_TXT=true
```

Then:
```bash
ytdlp-subs "URL" --cache-file "id_cache.txt"
```

## Behavior Changes

### None!

All functionality works exactly the same:

- ✅ Same subtitle download logic
- ✅ Same file naming
- ✅ Same caching mechanism
- ✅ Same VTT to TXT conversion
- ✅ Same rate limiting
- ✅ Same browser cookie support

## File Compatibility

### Cache Files

Old cache files work with new version:

```bash
# Your existing id_cache.txt works unchanged
ytdlp-subs "URL" --cache-file "id_cache.txt"
```

### Output Files

Same naming format:

```
0001_dQw4w9WgXcQ_Video_Title.hi.vtt
0002_jNQXAC9IVRw_Another_Video.en.txt
```

## Scripts Migration

### Bash Scripts

**Old:**
```bash
#!/bin/bash
sub-downloader "$1" \
  --lang "hi,en" \
  --output-dir "./subs" \
  --clean-txt
```

**New:**
```bash
#!/bin/bash
ytdlp-subs "$1" \
  --lang "hi,en" \
  --output-dir "./subs" \
  --clean-txt
```

### Cron Jobs

**Old:**
```cron
0 2 * * * /path/to/sub-downloader "URL" --cache-file /path/to/cache.txt
```

**New:**
```cron
0 2 * * * /path/to/.venv/bin/ytdlp-subs "URL" --cache-file /path/to/cache.txt
```

## Troubleshooting

### Command not found

```bash
# Reinstall
uv pip install -e .

# Or activate venv
source .venv/bin/activate
```

### Import errors

```bash
# Old imports don't work
from sub_downloader.main import main  # ❌

# Use new imports
from ytdlp_subs.presentation.cli import main  # ✅
```

### Old files interfering

```bash
# Remove old package
rm -rf src/sub_downloader
rm -rf src/sub_downloader.egg-info

# Reinstall
uv pip install -e .
```

## Rollback (If Needed)

If you need to rollback to old version:

```bash
# Checkout old code
git checkout <old-commit>

# Reinstall
pip install -e .

# Old command works again
sub-downloader "URL"
```

## Questions?

See [Usage Guide](usage-guide.md) for detailed examples.
