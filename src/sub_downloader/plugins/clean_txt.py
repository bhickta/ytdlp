import pathlib
import re
from .base import PostProcessPlugin

class CleanTxtPlugin(PostProcessPlugin):
    
    def run(self, vtt_path: pathlib.Path) -> pathlib.Path:
        """
        Reads a .vtt file, strips all timestamps and metadata,
        removes consecutive duplicate lines, and saves as a .txt file.
        The original .vtt file is then deleted.
        """
        txt_path = vtt_path.with_suffix('.txt')
        cleaned_lines = []
        last_line = None
        
        try:
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
            
            vtt_path.unlink() # Delete the original .vtt file
            print(f"    Successfully cleaned to: {txt_path.name}")
            return txt_path
            
        except (IOError, OSError) as e:
            print(f"    Error: Could not clean/write txt file: {e}", file=sys.stderr)
            return vtt_path # Return original path on failure