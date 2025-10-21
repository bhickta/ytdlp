import subprocess
import re

def run_command(command):
    return subprocess.run(
        command, 
        capture_output=True, 
        text=True, 
        check=True, 
        encoding='utf-8'
    )

def sanitize_filename(text):
    safe_text = re.sub(r'[\\/*?:"<>|]', '', text).strip()
    return safe_text[:100]