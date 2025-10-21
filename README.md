# YouTube Subtitle Downloader

A command-line tool to download all auto-generated subtitles (e.g., Hindi or English) from a specific YouTube channel.

## Features

- Downloads subtitles for an entire channel.
- Prefers specified languages (e.g., `hi`, then `en`).
- Skips video download, fetching only `.vtt` files.
- Creates a JSONL log file for resumability and auditing.
- Adds random delays between downloads to be polite to servers.

## Installation

1.  Ensure you have Python 3.8+ and `pip` installed.
2.  From the project root directory (`sub_downloader/`), install the tool in editable mode:

```bash
pip install -e .
```