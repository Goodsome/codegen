from abc import ABC, abstractmethod

from typing import Any, Dict


class TemplatePort(ABC):
    """
    Render templates with a given context.
    """
    
    @abstractmethod
    def render(self, template: str, context: Dict[str, Any]) -> str:
        """
        
        """
        pass
    