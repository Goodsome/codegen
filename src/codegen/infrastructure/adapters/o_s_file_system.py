from typing import List, Dict, Any, Optional
from codegen.domain.ports.file_system_port import FileSystemPort

class OSFileSystem(FileSystemPort):
    """
    OS file system adapter for reading/writing files.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        self.output_root = config.get("output_root", 'out')
        
        self.encoding = config.get("encoding", 'utf-8')
        

    
    def read_text(self, path: str) -> str:
        """
        
        """
        # TODO: Implement adapter logic
        pass
    
    def write_text(self, path: str, content: str) -> None:
        """
        
        """
        # TODO: Implement adapter logic
        pass
    
    def makedirs(self, path: str, exist_ok: bool) -> None:
        """
        
        """
        # TODO: Implement adapter logic
        pass
    