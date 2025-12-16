from typing import Protocol
from pathlib import Path

class FileSystemPort(Protocol):
    def write_file(self, path: Path, content: str) -> None:
        """写入文件，自动创建父目录"""
        ...

    def ensure_package(self, path: Path) -> None:
        """确保目录存在且包含 __init__.py"""
        ...