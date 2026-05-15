from abc import ABC, abstractmethod

from codegen.code_metadata.domain.aggregates.component import Component


class CodeParser(ABC):
    @abstractmethod
    def parse_code(self, code: str) -> Component: ...
