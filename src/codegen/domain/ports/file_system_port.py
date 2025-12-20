from abc import ABC, abstractmethod


class FileSystemPort(ABC):
    """
    File system operations used by the generator.
    """

    @abstractmethod
    def read_text(self, path: str) -> str:
        """ """
        pass

    @abstractmethod
    def write_text(self, path: str, content: str, overwrite: bool = False) -> None:
        """ """
        pass

    @abstractmethod
    def makedirs(self, path: str, exist_ok: bool) -> None:
        """ """
        pass
