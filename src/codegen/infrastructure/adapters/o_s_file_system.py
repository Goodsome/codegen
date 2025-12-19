from typing import List, Dict, Any, Optional
from pathlib import Path
from codegen.domain.ports.file_system_port import FileSystemPort

class OSFileSystem(FileSystemPort):
    """
    OS file system adapter for reading/writing files.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_root = Path(config.get("output_root", "out"))
        self.encoding = config.get("encoding", "utf-8")

    def read_text(self, relative_path: str) -> str:
        """
        Reads text from a file relative to output_root.
        """
        full_path = self.output_root / relative_path
        return full_path.read_text(encoding=self.encoding)
    
    def write_text(self, relative_path: str, content: str) -> None:
        """
        Writes text to a file relative to output_root.
        """
        full_path = self.output_root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding=self.encoding)
    
    def makedirs(self, relative_path: str, exist_ok: bool) -> None:
        """
        Creates directories relative to output_root.
        """
        full_path = self.output_root / relative_path
        full_path.mkdir(parents=True, exist_ok=exist_ok)
    