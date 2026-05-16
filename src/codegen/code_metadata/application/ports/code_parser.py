from abc import ABC, abstractmethod

from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent


class CodeParser(ABC):
    @abstractmethod
    def parse(self, code: str) -> ParsedComponent:
        pass
