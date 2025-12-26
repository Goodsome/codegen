from pathlib import Path
from typing import Dict, Any

from codegen.shared.domain.ports.file_system_port import FileSystemPort


class OSFileSystem(FileSystemPort):
    """
    OS file system adapter for reading/writing files.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        output_root = config.get("output_root", "target")
        if isinstance(output_root, str):
            self.output_root = Path(output_root)
        elif isinstance(output_root, Path):
            self.output_root = output_root
        else:
            raise ValueError("Invalid output_root value")
        self.encoding = config.get("encoding", "utf-8")

    def read_file(self, path: str) -> str:
        full_path = self.output_root / path
        return full_path.read_text(encoding=self.encoding)

    def write_file(self, path: Path, content: str, overwrite: bool = False) -> None:
        full_path = self.output_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if full_path.exists() and not overwrite:
            return
        full_path.write_text(content, encoding=self.encoding)
