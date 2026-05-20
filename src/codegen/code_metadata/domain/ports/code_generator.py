from abc import ABC, abstractmethod

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver


class CodeGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        component: Component,
        resolver: ReferenceResolver,
    ) -> str: ...
