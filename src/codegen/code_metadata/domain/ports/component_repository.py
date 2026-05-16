from abc import ABC, abstractmethod

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery
from codegen.shared.domain.ports.repository import Repository


class ComponentRepository(Repository[Component, ComponentId], ABC):
    """Component repository interface."""

    @abstractmethod
    def list(self, page_query: PageQuery[ComponentFilter]) -> Page[Component]: ...
        
