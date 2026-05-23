from abc import ABC, abstractmethod

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.services.translate_reference import TranslateReference


class CodeGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        component: Component,
        resolver: TranslateReference
    ) -> str: ...
