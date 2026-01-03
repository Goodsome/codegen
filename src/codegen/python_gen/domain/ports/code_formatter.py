from abc import (abstractmethod, ABC)




class CodeFormatter(ABC):
    """Formats Python source code."""
    
    
      
    @abstractmethod 
    def format_code(
        self, 
        code: str 
    ) -> str:
        
        ...
         
      


