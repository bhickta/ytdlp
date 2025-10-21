import subprocess
import json
import time
import random
import sys
import pathlib
import argparse

class SubtitleDownloader:

    def __init__(self, channel_url, lang_prefs_list, output_dir, min_wait, max_wait, cookies_from_browser, cache_file, force_refresh):
        self.channel_url = channel_url
        # This is now a list, e.g., ['en', 'hi']
        self.lang_prefs = lang_prefs_list
        self.output_path = pathlib.Path(output_dir)
        self.min_wait = min_wait
        self.max_wait = max_wait
        # Using the .json extension from your file
        self.log_file = self.output_path / "download_log.json"
        
        self.cookies_from_browser = cookies_from_browser 
        self.cache_file = pathlib.Path(cache_file) if cache_file else None
        self.force_refresh = force_refresh
        
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

    def _load_downloaded_ids(self):
        downloaded = set()
        if not self.log_file.exists():
            return downloaded
        
        print(f"Loading log file to find completed downloads...")
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get('status') == 'success' and 'video_id' in entry:
                            downloaded.add(entry['video_id'])
                    except json.JSONDecodeError:
                        pass 
        except IOError as e:
            print(f"Warning: Could not read log file '{self.log_file}': {e}", file=sys.stderr)
        
        return downloaded

    def fetch_video_ids(self):
        """
        Fetches video IDs, using a cache file if specified and available.
        """
        if self.cache_file and not self.force_refresh and self.cache_file.exists():
            print(f"Loading video list from cache: {self.cache_file}")
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    video_ids = [line.strip() for line in f if line.strip()]
                if video_ids:
                    print(f"Found {len(video_ids)} total videos in cache.")
                    return video_ids
                else:
                    print("Cache file is empty. Fetching from network.")
            except IOError as e:
                print(f"Warning: Could not read cache file. Fetching from network. Error: {e}")

        print(f"Fetching video list from network: {self.channel_url}...")
        command = ["yt-dlp", "--flat-playlist", "--print", "id", self.channel_url]
        
        try:
            result = self._run_command(command)
            video_ids = result.stdout.strip().split('\n')
            video_ids = [vid for vid in video_ids if vid.strip()]
            
            if not video_ids:
                print("No video IDs found. Check the channel URL.", file=sys.stderr)
                return []
                
            print(f"Found {len(video_ids)} total videos on channel.")
            
            if self.cache_file:
                # Ensure cache directory exists
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with open(self.cache_file, 'w', encoding='utf-8') as f:
                        for vid in video_ids:
                            f.write(vid + '\n')
                    print(f"Video list saved to cache: {self.cache_file}")
                except IOError as e:
                    print(f"Warning: Could not write to cache file '{self.cache_file}': {e}")
            
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
        """
        Tries to download subtitles for a video, one language at a time,
        based on the priority in self.lang_prefs.
        Stops and returns on the first successful download.
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Processing: {video_url}")
        
        log_data = {"video_id": video_id, "url": video_url}
        
        # --- NEW LOGIC: Loop through preferred languages ---
        for lang in self.lang_prefs:
            print(f"  Attempting to download language: {lang}")
            
            # This output template is cleaner and avoids the ".NA" problem.
            # It will produce "VIDEOID.en.vtt"
            output_template = str(self.output_path / "%(id)s.%(lang)s")
            
            command = [
                "yt-dlp",
                "--write-auto-sub",
                "--sub-lang", lang, # <--- Try only ONE language at a time
                "--skip-download",
                "--output", output_template, # <--- Use the clean template
                "--print-json",
            ]
            
            if self.cookies_from_browser:
                command.extend(["--cookies-from-browser", self.cookies_from_browser])
            
            command.append(video_url)
            
            try:
                result = self._run_command(command)
                json_output = result.stdout.strip().split('\n')[-1]
                video_meta = json.loads(json_output)
                
                requested_subs = video_meta.get("requested_subtitles", {})
                
                # Check if the specific language we asked for was downloaded
                if lang in requested_subs:
                    log_data["status"] = "success"
                    log_data["subtitle_language"] = lang
                    log_data["metadata"] = video_meta
                    print(f"    Success: Downloaded '{lang}' subs for {video_id}")
                    
                    # We found our preferred sub, so log and exit the function.
                    self._log_entry(log_data) 
                    return 
                
                # If it wasn't downloaded, loop continues to the next language
                print(f"    '{lang}' subs not available. Trying next language...")

            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip()
                # A 429 error (or any HTTP error) should stop processing this video
                if "HTTP Error" in error_msg:
                    log_data["status"] = "error"
                    log_data["error"] = error_msg
                    print(f"  Failed: {video_id} (Error: {error_msg})", file=sys.stderr)
                    self._log_entry(log_data)
                    return
                # Other errors (e.g., video private)
                print(f"    Warning (yt-dlp error): {error_msg}", file=sys.stderr)
                # Continue to next language if it's not a fatal error

            except json.JSONDecodeError as e:
                # This is a fatal error for this video
                log_data["status"] = "error"
                log_data["error"] = "Failed to parse yt-dlp JSON output."
                log_data["raw_output"] = result.stdout
                print(f"  Failed to parse output: {video_id}", file=sys.stderr)
                self._log_entry(log_data)
                return

        # --- END OF NEW LOGIC ---

        # If we went through the whole loop and found no subs
        print(f"  Warning: No '{','.join(self.lang_prefs)}' subs found for {video_id}.")
        log_data["status"] = "no_subs_found"
        log_data["metadata"] = None 
        self._log_entry(log_data)

    def run_downloader(self):
        downloaded_ids = self._load_downloaded_ids()
        if downloaded_ids:
            print(f"Found {len(downloaded_ids)} videos in log. Will skip duplicates.")

        all_video_ids = self.fetch_video_ids() # This uses the cache
        
        if not all_video_ids:
            print("No videos found or error occurred. Exiting.")
            return
            
        videos_to_download = [vid for vid in all_video_ids if vid not in downloaded_ids]
        
        total_all = len(all_video_ids)
        total_new = len(videos_to_download)
        total_skipped = total_all - total_new
        
        print(f"Total: {total_all}, Skipped: {total_skipped}, Remaining: {total_new}")
        
        if total_new == 0:
            print("All videos have already been processed. Exiting.")
            return

        for i, video_id in enumerate(videos_to_download, 1):
            print(f"\n--- Processing Video {i} of {total_new} ---")
            self.download_subtitle(video_id)
            
            if i < total_new:
                wait_time = random.uniform(self.min_wait, self.max_wait)
                print(f"  Waiting for {wait_time:.2f} seconds...")
                try:
                    time.sleep(wait_time)
                except KeyboardInterrupt:
                    print("\nInterrupted. Exiting gracefully.")
                    break
                    
        print(f"\nDownload process complete. Log file at: {self.log_file}")


def main():
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
    
    args = parser.parse_args()
    
    if args.min_wait > args.max_wait:
        print("Error: --min-wait cannot be greater than --max-wait.", file=sys.stderr)
        sys.exit(1)
    
    # --- CHANGE: Split lang string into a list ---
    lang_list = [lang.strip() for lang in args.lang_prefs.split(',') if lang.strip()]
    if not lang_list:
        print("Error: No languages specified in --lang.", file=sys.stderr)
        sys.exit(1)

    downloader = SubtitleDownloader(
        args.channel_url,
        lang_list, # <--- Pass the new list
        args.output_dir,
        args.min_wait,
        args.max_wait,
        args.cookies_from_browser,
        args.cache_file,
        args.force_refresh
    )
    try:
        downloader.run_downloader()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()