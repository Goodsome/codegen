from abc import ABC, abstractmethod

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver


class CodeGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        component: Component,
        resolver: ReferenceResolver,
    ) -> str: ...
