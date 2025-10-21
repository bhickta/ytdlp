import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Download auto-subtitles from a YouTube channel."
    )
    
    parser.add_argument(
        "channel_url", 
        help="The full URL of the YouTube channel's /videos page."
    )
    
    parser.add_argument(
        "--lang", 
        dest="lang_prefs",
        default="hi,en",
        help="Comma-separated language preferences (e.g., 'hi,en'). Default: 'hi,en'"
    )
    
    parser.add_argument(
        "--output-dir",
        default="subtitles",
        help="Directory to save subtitles and log. Default: 'subtitles'"
    )
    
    parser.add_argument(
        "--min-wait",
        type=float,
        default=5.0,
        help="Minimum random wait time between downloads (seconds). Default: 5"
    )
    
    parser.add_argument(
        "--max-wait",
        type=float,
        default=15.0,
        help="Maximum random wait time between downloads (seconds). Default: 15"
    )

    parser.add_argument(
        "--cookies-from-browser",
        help="Browser to use for cookies (e.g., 'chrome', 'firefox'). Fixes 429 errors."
    )
    
    parser.add_argument(
        "--cache-file",
        help="Path to a file to cache video IDs (e.g., 'my-subs/id_cache.txt')."
    )
    
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Ignore the cache file and re-fetch the video list from the network."
    )
    
    parser.add_argument(
        "--no-numbering",
        action="store_true",
        help="Disable prepending a sequential number (e.g., 0001_) to filenames."
    )
    
    parser.add_argument(
        "--clean-txt",
        action="store_true",
        help="Convert downloaded .vtt subtitles to .txt and remove all timestamps/metadata."
    )
    
    return parser.parse_args()