from abc import ABC, abstractmethod
from codegen.code_metadata.application.dtos.component_dto import ComponentDTO


class ComponentQueryService(ABC):
    
    @abstractmethod
    def find_by_name(self, name: str, context: str) -> ComponentDTO | None:
        pass