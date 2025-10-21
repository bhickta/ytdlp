import pathlib
from abc import ABC, abstractmethod

class PostProcessPlugin(ABC):
    """
    Base class for a post-processing plugin.
    Each plugin takes a file path and returns a new file path.
    """
    
    @abstractmethod
    def run(self, file_path: pathlib.Path) -> pathlib.Path:
        """
        Process the file and return the path to the new, processed file.
        The original file may be deleted by the plugin.
        """
        pass