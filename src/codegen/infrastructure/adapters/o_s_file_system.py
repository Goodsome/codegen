from pathlib import Path
from typing import Any, override

from codegen.domain.ports.file_system_port import FileSystemPort


class OSFileSystem(FileSystemPort):
    """
    OS file system adapter for reading/writing files.
    """

    def __init__(self, config: dict[str, Any]):
        self.config: dict[str, Any] = config
        self.output_root: Path = Path(config.get("output_root", "out"))
        self.encoding: str = config.get("encoding", "utf-8")

    def read_text(self, path: str) -> str:
        """
        Reads text from a file relative to output_root.
        """
        full_path = self.output_root / path
        return full_path.read_text(encoding=self.encoding)

    def write_text(self, path: str, content: str, overwrite: bool = False) -> None:
        """
        Writes text to a file relative to output_root.
        """
        full_path = self.output_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if full_path.exists() and not overwrite:
            return
        full_path.write_text(content, encoding=self.encoding)

    def makedirs(self, path: str, exist_ok: bool) -> None:
        """
        Creates directories relative to output_root.
        """
        full_path = self.output_root / path
        full_path.mkdir(parents=True, exist_ok=exist_ok)
