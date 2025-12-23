from abc import ABC, abstractmethod
from pathlib import Path


class FileSystemPort(ABC):
    """
    Port for interacting with the file system.
    """

    @abstractmethod
    def read_file(self, path: str) -> str: ...

    @abstractmethod
    def write_file(self, path: Path, content: str, overwrite: bool = False) -> None: ...
