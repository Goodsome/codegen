from abc import ABC, abstractmethod

from typing import Any, Dict


class TemplatePort(ABC):
    """
    Port for generating templates.
    """

    @abstractmethod
    def render(self, template_path: str, context: Dict[str, Any]) -> str: ...
