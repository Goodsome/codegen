from abc import ABC, abstractmethod
from pathlib import Path

from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent


class CodeParser(ABC):

    @abstractmethod
    def parse(self, code_path: Path) -> ParsedComponent:
        pass