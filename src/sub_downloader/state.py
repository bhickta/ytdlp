import pathlib
import re

class StateManager:
    def __init__(self, output_path: pathlib.Path):
        self.output_path = output_path
    
    def load_downloaded_ids(self) -> set:
        """
        Scans the output directory for downloaded files and extracts
        video IDs to determine what to skip.
        """
        downloaded = set()
        if not self.output_path.exists():
            return downloaded
        
        print(f"Scanning output directory to find completed downloads...")
        
        regex = re.compile(r"^(?:\d+_)?([a-zA-Z0-9_-]{11})_.*")

        for f in self.output_path.iterdir():
            if not f.is_file():
                continue
            
            match = regex.match(f.name)
            if match:
                video_id = match.group(1)
                downloaded.add(video_id)
        
        return downloaded