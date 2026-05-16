from dataclasses import dataclass

from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from codegen.code_metadata.application.services.dev_progress_service import DevProgressService
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.shared.application.dtos.page_query import PageQuery
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class GetDevProgress:
    uow: UnitOfWork[ComponentRepository]
    file_system_port: FileSystemPort
    dev_progress_service: DevProgressService

    def execute(self) -> DevProgress:
        with self.uow:
            page_query=PageQuery[ComponentFilter](
                current=1,
                size=None,
                condition=ComponentFilter(),
            )
            page = self.uow.repository.list(page_query=page_query)

        components: dict[str, Component] = {}
        for component in page.items:
            components[component.file_name] = component
            
        dp = self.dev_progress_service.get_dev_progress(components)
        return dp
