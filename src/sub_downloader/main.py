import sys
from .cli import parse_args
from .downloader import SubtitleDownloader

def main():
    args = parse_args()
    
    if args.min_wait > args.max_wait:
        print("Error: --min-wait cannot be greater than --max-wait.", file=sys.stderr)
        sys.exit(1)
    
    try:
        downloader = SubtitleDownloader(config=args)
        downloader.run()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: yt-dlp not found. Make sure it is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()