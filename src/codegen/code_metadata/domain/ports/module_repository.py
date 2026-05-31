from abc import ABC, abstractmethod

from codegen.code_metadata.application.dtos.module_filter import ModuleFilter
from codegen.code_metadata.domain.aggregates import Module
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery
from codegen.shared.domain.ports.repository import Repository


class ModuleRepository(Repository[Module, ModuleId], ABC):

    @abstractmethod
    def find_by_ids(self, ids: list[ModuleId]) -> dict[ModuleId, Module]: ...

    @abstractmethod
    def find_by_paths(self, paths: set[str]) -> dict[str, Module]: ...

    @abstractmethod
    def find_page(self, page_query: PageQuery[ModuleFilter]) -> Page[Module]: ...