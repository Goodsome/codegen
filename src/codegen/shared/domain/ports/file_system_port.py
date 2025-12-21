from abc import ABC, abstractmethod


class FileSystemPort(ABC):
    """
    Port for interacting with the file system.
    """
    
    @abstractmethod
    def read_file(
            self, 
            path: str
    ) -> str:
        
        ...
    
    @abstractmethod
    def write_file(
            self, 
            path: str, 
            content: str, 
            overwrite: bool
    ) -> None:
        
        ...
    