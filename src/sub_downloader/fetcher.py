import pathlib
import sys
import subprocess
from .utils import run_command

class VideoIDFetcher:
    def __init__(self, channel_url: str, cache_file: pathlib.Path, force_refresh: bool):
        self.channel_url = channel_url
        self.cache_file = cache_file
        self.force_refresh = force_refresh
        
    def fetch_video_ids(self) -> list:
        video_ids = self._load_ids_from_cache()
        if video_ids:
            return video_ids
        return self._fetch_ids_from_network()

    def _load_ids_from_cache(self) -> list | None:
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

    def _save_ids_to_cache(self, video_ids: list):
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

    def _fetch_ids_from_network(self) -> list:
        print(f"Fetching video list from network: {self.channel_url}...")
        command = ["yt-dlp", "--flat-playlist", "--print", "id", self.channel_url]
        
        try:
            result = run_command(command)
            video_ids = result.stdout.strip().split('\n')
            video_ids = [vid for vid in video_ids if vid.strip()]
            
            if video_ids:
                print(f"Found {len(video_ids)} total videos on channel.")
                self._save_ids_to_cache(video_ids)
                return video_ids
            
            print("No video IDs found. Check the channel URL.", file=sys.stderr)
            return []
            
        except subprocess.CalledProcessError as e:
            print(f"Error fetching video list: {e.stderr.strip()}", file=sys.stderr)
            return []