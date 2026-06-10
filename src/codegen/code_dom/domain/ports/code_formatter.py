from abc import ABC, abstractmethod


class CodeFormatter(ABC):
    """Formats Python source code."""

    @abstractmethod
    def format_code(self, code: str) -> str: ...
