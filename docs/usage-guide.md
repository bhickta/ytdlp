# Usage Guide

Comprehensive examples for all features.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Language Selection](#language-selection)
- [Output Configuration](#output-configuration)
- [Rate Limiting](#rate-limiting)
- [Caching](#caching)
- [File Processing](#file-processing)
- [Browser Cookies](#browser-cookies)
- [Logging](#logging)
- [Advanced Scenarios](#advanced-scenarios)

## Basic Usage

### Download from Channel

```bash
ytdlp-subs "https://www.youtube.com/@channelname/videos"
```

**What happens:**
- Fetches all video IDs from channel
- Downloads Hindi subtitles (default)
- Falls back to English if Hindi unavailable
- Saves to `./subtitles/` directory
- Files named: `0001_videoID_title.hi.vtt`

### Specify Output Directory

```bash
ytdlp-subs "URL" --output-dir /path/to/subtitles
```

**Result:** All files saved to `/path/to/subtitles/`

## Language Selection

### Single Language

```bash
# Only English
ytdlp-subs "URL" --lang en
```

### Multiple Languages (Priority Order)

```bash
# Try Spanish first, then English, then Hindi
ytdlp-subs "URL" --lang es,en,hi
```

**Behavior:**
- Tries Spanish first
- If unavailable, tries English
- If unavailable, tries Hindi
- If none available, skips video

### Supported Languages

Common language codes:
- `hi` - Hindi
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese

## Output Configuration

### Disable Sequential Numbering

```bash
ytdlp-subs "URL" --no-numbering
```

**Without numbering:**
```
videoID_title.hi.vtt
anotherID_title.en.vtt
```

**With numbering (default):**
```
0001_videoID_title.hi.vtt
0002_anotherID_title.en.vtt
```

### Clean Text Output

Convert VTT to clean text (removes timestamps, HTML tags, duplicates):

```bash
ytdlp-subs "URL" --clean-txt
```

**Input (VTT):**
```
WEBVTT

00:00:01.000 --> 00:00:03.000
<c>Hello world</c>

00:00:03.000 --> 00:00:05.000
Hello world

00:00:05.000 --> 00:00:07.000
Welcome to the video
```

**Output (TXT):**
```
Hello world
Welcome to the video
```

## Rate Limiting

### Default Behavior

Default: 5-15 seconds random wait between downloads

### Custom Wait Times

```bash
# Wait 3-10 seconds between downloads
ytdlp-subs "URL" --min-wait 3 --max-wait 10

# No wait (not recommended)
ytdlp-subs "URL" --min-wait 0 --max-wait 0

# Conservative (20-30 seconds)
ytdlp-subs "URL" --min-wait 20 --max-wait 30
```

**Why rate limiting?**
- Prevents IP bans
- Respectful to YouTube servers
- Avoids 429 (Too Many Requests) errors

## Caching

### Enable Caching

```bash
ytdlp-subs "URL" --cache-file ./video-cache.txt
```

**Benefits:**
- Faster reruns (no network fetch)
- Resume interrupted downloads
- Consistent video order

### Cache Workflow

**First run:**
```bash
ytdlp-subs "URL" --cache-file ./cache.txt
# Fetches from network, saves to cache
# Downloads subtitles
```

**Second run:**
```bash
ytdlp-subs "URL" --cache-file ./cache.txt
# Loads from cache (instant)
# Only downloads new videos
```

**Force refresh:**
```bash
ytdlp-subs "URL" --cache-file ./cache.txt --force-refresh
# Ignores cache, fetches fresh list
# Updates cache
```

### Cache File Format

Simple text file with one video ID per line:

```
dQw4w9WgXcQ
jNQXAC9IVRw
oHg5SJYRHA0
```

## File Processing

### Filename Format

**Default format:**
```
{index}_{videoID}_{sanitized_title}.{language}.{format}
```

**Examples:**
```
0001_dQw4w9WgXcQ_Never_Gonna_Give_You_Up.hi.vtt
0002_jNQXAC9IVRw_Me_at_the_zoo.en.vtt
```

**Without numbering:**
```
dQw4w9WgXcQ_Never_Gonna_Give_You_Up.hi.vtt
jNQXAC9IVRw_Me_at_the_zoo.en.vtt
```

### Title Sanitization

Invalid characters removed: `\ / * ? : " < > |`

**Original:** `"Video: Part 1/2 <HD>"`
**Sanitized:** `Video Part 12 HD`

## Browser Cookies

### Why Use Cookies?

Fixes 429 (Too Many Requests) errors by authenticating as logged-in user.

### Chrome

```bash
ytdlp-subs "URL" --cookies-from-browser chrome
```

### Firefox

```bash
ytdlp-subs "URL" --cookies-from-browser firefox
```

### Other Browsers

Supported: `chrome`, `firefox`, `edge`, `safari`, `opera`, `brave`

**Note:** Browser must be installed and you must be logged into YouTube.

## Logging

### Log Levels

```bash
# Debug (very verbose)
ytdlp-subs "URL" --log-level DEBUG

# Info (default)
ytdlp-subs "URL" --log-level INFO

# Warning (only warnings/errors)
ytdlp-subs "URL" --log-level WARNING

# Error (only errors)
ytdlp-subs "URL" --log-level ERROR
```

### Log to File

```bash
ytdlp-subs "URL" --log-file ./download.log
```

**Log file content:**
```json
{"timestamp": "2026-01-29T18:30:00", "level": "INFO", "event": "Downloading subtitle", "video_id": "dQw4w9WgXcQ"}
{"timestamp": "2026-01-29T18:30:05", "level": "INFO", "event": "Successfully downloaded", "video_id": "dQw4w9WgXcQ"}
```

### Combined Logging

```bash
ytdlp-subs "URL" \
  --log-level DEBUG \
  --log-file ./debug.log
```

## Advanced Scenarios

### Scenario 1: Large Educational Channel

**Requirements:**
- 500+ videos
- Need clean text for processing
- Want to resume if interrupted
- Avoid rate limiting

**Solution:**
```bash
ytdlp-subs "https://www.youtube.com/@edu/videos" \
  --output-dir ./edu-transcripts \
  --lang en \
  --clean-txt \
  --cache-file ./edu-cache.txt \
  --min-wait 10 \
  --max-wait 20 \
  --cookies-from-browser chrome \
  --log-file ./edu-download.log
```

### Scenario 2: Multi-language News Channel

**Requirements:**
- Download Spanish and English
- Organize by language
- Fast processing

**Solution:**
```bash
# Spanish subtitles
ytdlp-subs "https://www.youtube.com/@news/videos" \
  --output-dir ./news/spanish \
  --lang es \
  --min-wait 3 \
  --max-wait 8

# English subtitles
ytdlp-subs "https://www.youtube.com/@news/videos" \
  --output-dir ./news/english \
  --lang en \
  --min-wait 3 \
  --max-wait 8
```

### Scenario 3: Research Data Collection

**Requirements:**
- Download from multiple channels
- Consistent naming
- Track progress
- Handle failures gracefully

**Solution:**
```bash
#!/bin/bash
# download-all.sh

CHANNELS=(
  "https://www.youtube.com/@channel1/videos"
  "https://www.youtube.com/@channel2/videos"
  "https://www.youtube.com/@channel3/videos"
)

for channel in "${CHANNELS[@]}"; do
  channel_name=$(echo $channel | sed 's/.*@\(.*\)\/videos/\1/')
  
  echo "Processing: $channel_name"
  
  ytdlp-subs "$channel" \
    --output-dir "./research/$channel_name" \
    --lang en,hi \
    --clean-txt \
    --cache-file "./cache/$channel_name.txt" \
    --log-file "./logs/$channel_name.log" \
    --min-wait 5 \
    --max-wait 15
  
  echo "Completed: $channel_name"
  sleep 60  # Wait between channels
done
```

### Scenario 4: Incremental Updates

**Requirements:**
- Daily download of new videos
- Skip already downloaded
- Maintain cache

**Solution:**
```bash
# Run daily via cron
0 2 * * * /path/to/ytdlp-subs "URL" \
  --cache-file /path/to/cache.txt \
  --output-dir /path/to/subtitles \
  --log-file /path/to/daily.log
```

**How it works:**
1. Loads cached video list
2. Checks which videos already have subtitles
3. Only downloads new videos
4. Updates cache with any new videos

## Environment Variables

Set defaults via environment variables:

```bash
export YTDLP_SUBS_LANGUAGE_PREFERENCES="hi,en"
export YTDLP_SUBS_OUTPUT_DIR="./subtitles"
export YTDLP_SUBS_MIN_WAIT_SECONDS=5.0
export YTDLP_SUBS_MAX_WAIT_SECONDS=15.0

# Now just run with channel URL
ytdlp-subs "URL"
```

## Troubleshooting

### Error: 429 Too Many Requests

**Solution:** Use browser cookies
```bash
ytdlp-subs "URL" --cookies-from-browser chrome
```

### Error: yt-dlp not found

**Solution:** Install yt-dlp
```bash
pip install yt-dlp
```

### Error: No subtitles found

**Causes:**
- Channel has no auto-generated subtitles
- Language not available

**Solution:** Try different language
```bash
ytdlp-subs "URL" --lang en,hi,es,fr
```

### Slow Performance

**Solutions:**
- Reduce wait times (carefully)
- Use caching
- Check internet connection

## Tips & Best Practices

1. **Always use caching** for channels with 100+ videos
2. **Use browser cookies** if you hit rate limits
3. **Start with conservative rate limits** (10-20s), then reduce if stable
4. **Use clean-txt** if you need text processing
5. **Enable logging** for debugging issues
6. **Test with small channels** before large ones
7. **Use environment variables** for repeated tasks
