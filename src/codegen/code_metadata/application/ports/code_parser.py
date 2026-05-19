from abc import ABC, abstractmethod
from pathlib import Path

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent


class CodeParser(ABC):
    @abstractmethod
    def parse(self, code: str, component_name: str) -> ParsedComponent: ...

    @abstractmethod
    def parse_dependencies(self, code: str, component_path: Path) -> set[ImportedComponent]: ...
