import subprocess
import json
import time
import random
import sys
import pathlib
import argparse

class SubtitleDownloader:

    def __init__(self, channel_url, lang_prefs, output_dir, min_wait, max_wait):
        self.channel_url = channel_url
        self.lang_prefs = lang_prefs
        self.output_path = pathlib.Path(output_dir)
        self.min_wait = min_wait
        self.max_wait = max_wait
        # Log file is now relative to the output path
        self.log_file = self.output_path / "download_log.jsonl"
        
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Fatal: Could not create output directory '{output_dir}': {e}", file=sys.stderr)
            sys.exit(1)

    def _run_command(self, command):
        return subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            encoding='utf-8'
        )

    def _log_entry(self, log_data):
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data) + '\n')
        except IOError as e:
            print(f"Warning: Could not write to log file: {e}", file=sys.stderr)

    def fetch_video_ids(self):
        print(f"Fetching video list for {self.channel_url}...")
        command = ["yt-dlp", "--flat-playlist", "--print", "id", self.channel_url]
        
        try:
            result = self._run_command(command)
            video_ids = result.stdout.strip().split('\n')
            video_ids = [vid for vid in video_ids if vid.strip()]
            
            if not video_ids:
                print("No video IDs found. Check the channel URL.", file=sys.stderr)
                return []
                
            print(f"Found {len(video_ids)} videos.")
            return video_ids
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip()
            print(f"Error fetching video list: {error_msg}", file=sys.stderr)
            self._log_entry({"status": "error", "task": "fetch_list", "error": error_msg})
            return []
        except FileNotFoundError:
            print("Error: yt-dlp not found. Make sure it is installed and in your PATH.", file=sys.stderr)
            sys.exit(1)

    def download_subtitle(self, video_id):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Processing: {video_url}")
        
        output_template = str(self.output_path / "%(id)s.%(lang)s")
        
        command = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", self.lang_prefs,
            "--skip-download",
            "--output", output_template,
            "--dump-json",
            video_url
        ]
        
        log_data = {"video_id": video_id, "url": video_url}
        
        try:
            result = self._run_command(command)
            video_meta = json.loads(result.stdout)
            log_data["status"] = "success"
            log_data["metadata"] = video_meta
            
            subs = video_meta.get("automatic_captions", {}).keys()
            print(f"  Success: {video_id} (Available: {list(subs)})")
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip()
            log_data["status"] = "error"
            log_data["error"] = error_msg
            print(f"  Failed: {video_id} (Error: {error_msg})", file=sys.stderr)
            
        except json.JSONDecodeError as e:
            log_data["status"] = "error"
            log_data["error"] = "Failed to parse yt-dlp JSON output."
            log_data["raw_output"] = result.stdout
            print(f"  Failed to parse output: {video_id}", file=sys.stderr)
            
        finally:
            self._log_entry(log_data)

    def run_downloader(self):
        video_ids = self.fetch_video_ids()
        
        if not video_ids:
            print("No videos found or error occurred. Exiting.")
            return
            
        total = len(video_ids)
        for i, video_id in enumerate(video_ids, 1):
            print(f"\n--- Video {i} of {total} ---")
            self.download_subtitle(video_id)
            
            if i < total:
                wait_time = random.uniform(self.min_wait, self.max_wait)
                print(f"  Waiting for {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                
        print(f"\nDownload process complete. Log file at: {self.log_file}")


def main():
    """Main function to run the CLI."""
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
    
    args = parser.parse_args()
    
    if args.min_wait > args.max_wait:
        print("Error: --min-wait cannot be greater than --max-wait.", file=sys.stderr)
        sys.exit(1)

    downloader = SubtitleDownloader(
        args.channel_url,
        args.lang_prefs,
        args.output_dir,
        args.min_wait,
        args.max_wait
    )
    downloader.run_downloader()

if __name__ == "__main__":
    main()