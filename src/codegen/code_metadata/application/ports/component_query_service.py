from abc import ABC, abstractmethod
from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


class ComponentQueryService(ABC):
    
    @abstractmethod
    def find_by_name(self, name: str, context: str) -> ComponentDTO | None:
        pass

    @abstractmethod
    def list(self, query: PageQuery[ComponentFilter]) -> Page[ComponentDTO]:
        pass