import subprocess
import json
import time
import random
import sys
import pathlib
from .utils import run_command
from .fetcher import VideoIDFetcher
from .state import StateManager
from .file_processor import FileProcessor

class SubtitleDownloader:

    def __init__(self, config):
        self.config = config
        self.output_path = pathlib.Path(config.output_dir)
        self.lang_prefs = [lang.strip() for lang in config.lang_prefs.split(',') if lang.strip()]
        
        # Compose the downloader from its components
        self.fetcher = VideoIDFetcher(
            channel_url=config.channel_url,
            cache_file=pathlib.Path(config.cache_file) if config.cache_file else None,
            force_refresh=config.force_refresh
        )
        self.state_manager = StateManager(self.output_path)
        self.processor = FileProcessor(
            output_path=self.output_path,
            numbering_enabled=not config.no_numbering,
            clean_txt=config.clean_txt
        )

    def run(self):
        downloaded_ids = self.state_manager.load_downloaded_ids()
        all_video_ids = self.fetcher.fetch_video_ids()
        
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

    def _process_download_queue(self, all_video_ids, downloaded_ids, total_new_videos):
        current_new_index = 0
        total_all_videos = len(all_video_ids)

        for global_index, video_id in enumerate(all_video_ids, 1):
            if video_id in downloaded_ids:
                continue
            
            current_new_index += 1
            print(f"\n--- Processing Video {current_new_index} of {total_new_videos} (Global Index: {global_index}) ---")
            
            self._download_subtitle(video_id, global_index, total_all_videos) 
            
            if current_new_index < total_new_videos:
                self._wait_random_time()
                
    def _wait_random_time(self):
        wait_time = random.uniform(self.config.min_wait, self.config.max_wait)
        print(f"  Waiting for {wait_time:.2f} seconds...")
        try:
            time.sleep(wait_time)
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting gracefully.")
            sys.exit(0)

    def _download_subtitle(self, video_id, current_index, total_for_padding):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Processing: {video_url}")
        
        for lang in self.lang_prefs:
            print(f"  Attempting to download language: {lang}")
            
            temp_template_base = self.output_path / f"{video_id}_{lang}.temp"
            video_meta, temp_file = self._execute_yt_dlp_for_lang(video_id, lang, temp_template_base)
            
            if video_meta == "fatal_error":
                return

            if video_meta and temp_file and temp_file.exists():
                self.processor.process_file(
                    temp_file=temp_file,
                    video_meta=video_meta,
                    lang=lang,
                    current_index=current_index,
                    total_for_padding=total_for_padding
                )
                return
            elif temp_file and not temp_file.exists():
                print(f"    Error: Temp file '{temp_file}' not found. Cannot rename.")
            elif not video_meta:
                pass
        
        print(f"  Warning: No '{','.join(self.lang_prefs)}' subs found for {video_id}.")

    def _execute_yt_dlp_for_lang(self, video_id, lang, temp_template_base):
        temp_template = str(temp_template_base)
        command = self._build_yt_dlp_command(video_id, lang, temp_template)
        
        try:
            result = run_command(command)
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
            print(f"  Failed: {video_id} (Error: {e.stderr.strip()})", file=sys.stderr)
            return "fatal_error", None 
        except json.JSONDecodeError:
            print(f"  Failed to parse output: {video_id}", file=sys.stderr)
            return "fatal_error", None

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
        
        if self.config.cookies_from_browser:
            command.extend(["--cookies-from-browser", self.config.cookies_from_browser])
        
        command.append(video_url)
        return command