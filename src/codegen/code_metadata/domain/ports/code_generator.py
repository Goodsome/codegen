from abc import ABC, abstractmethod

from codegen.code_metadata.domain.aggregates.component import Component


class CodeGenerator(ABC):
    @abstractmethod
    def generate(self, component: Component) -> str: ...
