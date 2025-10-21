import pathlib
from .utils import sanitize_filename
from .plugins.clean_txt import CleanTxtPlugin

class FileProcessor:
    def __init__(self, output_path: pathlib.Path, numbering_enabled: bool, clean_txt: bool):
        self.output_path = output_path
        self.numbering_enabled = numbering_enabled
        
        # This is the "plugin" system.
        # We load the plugins that were requested by the config.
        self.plugins = []
        if clean_txt:
            self.plugins.append(CleanTxtPlugin())
            
    def _rename_file(self, temp_file: pathlib.Path, video_meta: dict, lang: str, 
                     current_index: int, total_for_padding: int) -> pathlib.Path:
        
        title = video_meta.get('title', 'UnknownTitle')
        safe_title = sanitize_filename(title)
        video_id = video_meta.get('id', 'UnknownID')
        
        base_name = f"{video_id}_{safe_title}"
        if self.numbering_enabled:
            padding = len(str(total_for_padding))
            prefix = str(current_index).zfill(padding)
            base_name = f"{prefix}_{base_name}"
        
        ext = temp_file.suffix
        final_name = f"{base_name}.{lang}{ext}"
        final_file_path = self.output_path / final_name

        temp_file.rename(final_file_path)
        print(f"    Renamed file to: {final_name}")
        return final_file_path
        
    def process_file(self, temp_file: pathlib.Path, video_meta: dict, lang: str, 
                     current_index: int, total_for_padding: int) -> str:
        """
        Renames and runs all post-processing plugins on the downloaded file.
        Returns the final filename.
        """
        try:
            final_path = self._rename_file(temp_file, video_meta, lang, current_index, total_for_padding)
            
            # Run all loaded plugins sequentially
            for plugin in self.plugins:
                final_path = plugin.run(final_path)
                
            return final_path.name
            
        except (OSError, IOError) as e:
            print(f"    Error: Failed to process file: {e}", file=sys.stderr)
            return ""