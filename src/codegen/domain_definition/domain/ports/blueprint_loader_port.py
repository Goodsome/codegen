from abc import ABC, abstractmethod
from typing import Union
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint




class BlueprintLoaderPort(ABC):
    """Loads the blueprint from a file."""
    
    
      
    @abstractmethod 
    def load(
        self, 
        source: str 
    ) -> Blueprint | None:
        ...
         
      

