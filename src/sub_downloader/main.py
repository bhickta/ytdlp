import subprocess
import json
import time
import random
import sys
import pathlib
import argparse
import re

class SubtitleDownloader:

    def __init__(self, config):
        self.channel_url = config.channel_url
        self.lang_prefs = [lang.strip() for lang in config.lang_prefs.split(',') if lang.strip()]
        self.output_path = pathlib.Path(config.output_dir)
        self.min_wait = config.min_wait
        self.max_wait = config.max_wait
        
        self.cookies_from_browser = config.cookies_from_browser
        self.cache_file = pathlib.Path(config.cache_file) if config.cache_file else None
        self.force_refresh = config.force_refresh
        self.numbering_enabled = not config.no_numbering
        self.clean_txt = config.clean_txt
        
        self.output_path.mkdir(parents=True, exist_ok=True)
        if not self.lang_prefs:
            print("Error: No languages specified in --lang.", file=sys.stderr)
            sys.exit(1)

    def _run_command(self, command):
        return subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            encoding='utf-8'
        )

    def _clean_vtt_to_txt(self, vtt_path):
        txt_path = vtt_path.with_suffix('.txt')
        cleaned_lines = []
        last_line = None
        
        with open(vtt_path, 'r', encoding='utf-8') as f_vtt:
            for line in f_vtt:
                line = line.strip()
                
                if not line or '-->' in line or line.isdigit():
                    continue
                if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                    continue
                    
                line = re.sub(r'<[^>]+>', '', line).strip()
                
                if line and line != last_line:
                    cleaned_lines.append(line)
                    last_line = line
                        
        with open(txt_path, 'w', encoding='utf-8') as f_txt:
            f_txt.write('\n'.join(cleaned_lines))
            
        return txt_path

    def _load_downloaded_ids(self):
        """
        Scans the output directory for downloaded files and extracts
        video IDs to determine what to skip.
        """
        downloaded = set()
        if not self.output_path.exists():
            return downloaded
        
        print(f"Scanning output directory to find completed downloads...")
        
        # Regex: Optionally match "001_" at the start, then capture 11 chars.
        regex = re.compile(r"^(?:\d+_)?([a-zA-Z0-9_-]{11})_.*")

        for f in self.output_path.iterdir():
            if not f.is_file():
                continue
            
            match = regex.match(f.name)
            if match:
                video_id = match.group(1) # Group 1 is the 11-char ID
                downloaded.add(video_id)
        
        return downloaded

    def _load_ids_from_cache(self):
        if self.cache_file and not self.force_refresh and self.cache_file.exists():
            print(f"Loading video list from cache: {self.cache_file}")
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    video_ids = [line.strip() for line in f if line.strip()]
                if video_ids:
                    print(f"Found {len(video_ids)} total videos in cache.")
                    return video_ids
                print("Cache file is empty. Fetching from network.")
            except IOError as e:
                print(f"Warning: Could not read cache file. Fetching from network. Error: {e}")
        return None

    def _save_ids_to_cache(self, video_ids):
        if not self.cache_file:
            return
        
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                for vid in video_ids:
                    f.write(vid + '\n')
            print(f"Video list saved to cache: {self.cache_file}")
        except IOError as e:
            print(f"Warning: Could not write to cache file '{self.cache_file}': {e}")

    def _fetch_ids_from_network(self):
        print(f"Fetching video list from network: {self.channel_url}...")
        command = ["yt-dlp", "--flat-playlist", "--print", "id", self.channel_url]
        
        try:
            result = self._run_command(command)
            video_ids = result.stdout.strip().split('\n')
            video_ids = [vid for vid in video_ids if vid.strip()]
            
            if video_ids:
                print(f"Found {len(video_ids)} total videos on channel.")
                self._save_ids_to_cache(video_ids)
                return video_ids
            
            print("No video IDs found. Check the channel URL.", file=sys.stderr)
            return []
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip()
            print(f"Error fetching video list: {error_msg}", file=sys.stderr)
            return []
        except FileNotFoundError:
            print("Error: yt-dlp not found. Make sure it is installed and in your PATH.", file=sys.stderr)
            sys.exit(1)

    def fetch_video_ids(self):
        video_ids = self._load_ids_from_cache()
        if video_ids:
            return video_ids
        return self._fetch_ids_from_network()

    def _build_yt_dlp_command(self, video_id, lang, temp_template):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        command = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", lang,
            "--skip-download",
            "--output", temp_template,
            "--print-json",
        ]
        
        if self.cookies_from_browser:
            command.extend(["--cookies-from-browser", self.cookies_from_browser])
        
        command.append(video_url)
        return command

    def _execute_yt_dlp_for_lang(self, video_id, lang, temp_template_base):
        
        temp_template = str(temp_template_base)
        command = self._build_yt_dlp_command(video_id, lang, temp_template)
        
        try:
            result = self._run_command(command)
            json_output = result.stdout.strip().split('\n')[-1]
            video_meta = json.loads(json_output)
            
            requested_subs = video_meta.get("requested_subtitles", {})
            
            if lang in requested_subs:
                ext = requested_subs[lang].get('ext', 'vtt')
                
                temp_file = self.output_path / f"{video_id}_{lang}.temp.{lang}.{ext}"
                
                return video_meta, temp_file
            
            print(f"    '{lang}' subs not available. Trying next language...")
            return None, None

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip()
            print(f"  Failed: {video_id} (Error: {error_msg})", file=sys.stderr)
            return "fatal_error", None 
        except json.JSONDecodeError as e:
            print(f"  Failed to parse output: {video_id}", file=sys.stderr)
            return "fatal_error", None

    def _sanitize_filename(self, text):
        safe_text = re.sub(r'[\\/*?:"<>|]', '', text).strip()
        return safe_text[:100]

    def _rename_file(self, temp_file, video_meta, lang, current_index, total_for_padding):
        title = video_meta.get('title', 'UnknownTitle')
        safe_title = self._sanitize_filename(title)
        video_id = video_meta.get('id', 'UnknownID')
        
        base_name = f"{video_id}_{safe_title}"
        if self.numbering_enabled:
            padding = len(str(total_for_padding))
            prefix = str(current_index).zfill(padding)
            base_name = f"{prefix}_{base_name}"
        
        ext = temp_file.suffix # Gets the LAST extension, e.g., ".vtt"
        final_name = f"{base_name}.{lang}{ext}"
        
        final_file_path = self.output_path / final_name

        temp_file.rename(final_file_path)
        print(f"    Renamed file to: {final_name}")
        return final_file_path

    def download_subtitle(self, video_id, current_index, total_for_padding):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Processing: {video_url}")
        
        for lang in self.lang_prefs:
            print(f"  Attempting to download language: {lang}")
            
            temp_template_base = self.output_path / f"{video_id}_{lang}.temp"
            
            video_meta, temp_file = self._execute_yt_dlp_for_lang(video_id, lang, temp_template_base)
            
            if video_meta == "fatal_error":
                return

            if video_meta and temp_file and temp_file.exists():
                try:
                    final_path = self._rename_file(temp_file, video_meta, lang, current_index, total_for_padding)
                    final_name = final_path.name
                    
                    if self.clean_txt:
                        txt_path = self._clean_vtt_to_txt(final_path)
                        final_path.unlink()
                        final_name = txt_path.name
                        print(f"    Successfully cleaned to: {final_name}")
                    
                    return
                except (OSError, IOError) as e:
                    print(f"    Error: Failed to process file: {e}", file=sys.stderr)
                    return
            elif temp_file and not temp_file.exists():
                print(f"    Error: Temp file '{temp_file}' not found. Cannot rename.")
            elif not video_meta:
                pass # Already logged 'not available'
        
        print(f"  Warning: No '{','.join(self.lang_prefs)}' subs found for {video_id}.")

    def _process_download_queue(self, all_video_ids, downloaded_ids, total_new_videos):
        """
        Processes videos, using the global index for numbering and
        a separate counter for the "X of Y" progress message.
        """
        current_new_index = 0
        total_all_videos = len(all_video_ids) # For padding

        for global_index, video_id in enumerate(all_video_ids, 1):
            if video_id in downloaded_ids:
                continue
            
            current_new_index += 1
            print(f"\n--- Processing Video {current_new_index} of {total_new_videos} (Global Index: {global_index}) ---")
            
            self.download_subtitle(video_id, global_index, total_all_videos) 
            
            if current_new_index < total_new_videos:
                wait_time = random.uniform(self.min_wait, self.max_wait)
                print(f"  Waiting for {wait_time:.2f} seconds...")
                try:
                    time.sleep(wait_time)
                except KeyboardInterrupt:
                    print("\nInterrupted. Exiting gracefully.")
                    break
        
    def run(self):
        """
        Main execution function.
        """
        downloaded_ids = self._load_downloaded_ids()
        all_video_ids = self.fetch_video_ids()
        
        if not all_video_ids:
            print("No videos found or error occurred. Exiting.")
            return
            
        videos_to_download = [vid for vid in all_video_ids if vid not in downloaded_ids]
        
        total_all = len(all_video_ids)
        total_new = len(videos_to_download)
        total_skipped = total_all - total_new
        
        print(f"Total: {total_all}, Skipped: {total_skipped}, Remaining: {total_new}")
        
        if not videos_to_download:
            print("All videos have already been processed. Exiting.")
            return
            
        self._process_download_queue(all_video_ids, downloaded_ids, total_new)
        print(f"\nDownload process complete.")

def _parse_args():
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

def main():
    args = _parse_args()
    
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