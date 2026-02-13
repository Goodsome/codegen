from pathlib import Path
from typing import Any, Dict, Iterator, override

from codegen.shared.domain.ports.file_system_port import FileSystemPort


class OSFileSystem(FileSystemPort):
    """
    OS file system adapter for reading/writing files.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        output_root = config.get("output_root", "target")
        if isinstance(output_root, str):
            self.root = Path(output_root)
        elif isinstance(output_root, Path):
            self.root = output_root
        else:
            raise ValueError("Invalid output_root value")
        self.encoding = config.get("encoding", "utf-8")

    def read_file(self, path: Path) -> str:
        full_path = self.root / path
        return full_path.read_text(encoding=self.encoding)

    def write_file(self, path: Path, content: str, overwrite: bool = False) -> bool:
        """
        Writes content to file.
        Returns True if written, False if skipped (due to overwrite=False).
        """
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if full_path.exists() and not overwrite:
            return False
        _ = full_path.write_text(content, encoding=self.encoding)
        return True

    def list_directory_recursively(self, path: Path) -> Iterator[Path]:
        return self.root.glob(str(path / "**" / "*"))

    def list_directory_flat(self, path: Path) -> Iterator[Path]:
        full_path = self.root / path
        for entry in full_path.iterdir():
            yield entry.relative_to(self.root)

    def is_directory(self, path: Path) -> bool:
        return (self.root / path).is_dir()

    def is_file(self, path: Path) -> bool:
        return (self.root / path).is_file()

    def exists(self, path: Path) -> bool:
        return (self.root / path).exists()
