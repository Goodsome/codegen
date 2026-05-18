from abc import ABC, abstractmethod

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent


class CodeParser(ABC):
    @abstractmethod
    def parse(self, code: str, component_name: str) -> ParsedComponent: ...

    @abstractmethod
    def parse_dependencies(self, code: str) -> set[ImportedComponent]: ...
