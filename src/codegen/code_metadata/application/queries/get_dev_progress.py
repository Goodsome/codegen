from dataclasses import dataclass

from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from codegen.code_metadata.application.dtos.get_dev_progress_query import (
    GetDevProgressQuery,
)
from codegen.code_metadata.application.services.dev_progress_service import (
    DevProgressService,
)
from codegen.code_metadata.application.services.memory_component_collection import MemoryComponentCollection
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.shared.application.dtos.page_query import PageQuery
from codegen.shared.application.ports.unit_of_work import UnitOfWork


@dataclass
class GetDevProgress:
    
    uow: UnitOfWork[ComponentRepository]
    dev_progress_service: DevProgressService

    def execute(self, query: GetDevProgressQuery) -> DevProgress:
        with self.uow:
            page_query = PageQuery[ComponentFilter](
                current=1,
                size=None,
                condition=ComponentFilter(
                    context=query.context,
                    type=query.component_type,
                    name=query.component_name,
                ),
            )
            page = self.uow.repository.find_page(page_query=page_query)


            components: dict[str, Component] = {}
            dependencies: set[ComponentId] = set()
            for component in page.items:
                components[component.file_name] = component
                dependencies.update(component.get_dependencies())
            
            deps = self.uow.repository.find_by_ids(dependencies)

        dp = self.dev_progress_service.get_dev_progress(
            context=query.context,
            components=components,
            components_depdencies=deps
        )
        return dp
