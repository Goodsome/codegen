from dataclasses import dataclass

from codegen.code_metadata.application.dtos.upsert_component_command import UpsertComponentCommand
from codegen.code_metadata.application.mappers.component_mapper import ComponentDTOMapper
from codegen.code_metadata.application.ports.component_query_service import ComponentQueryService
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork


@dataclass
class UpsertComponents:
    uow: UnitOfWork[ComponentRepository]
    query_service: ComponentQueryService
    component_mapper: ComponentDTOMapper

    def execute(self, cmd: list[UpsertComponentCommand]) -> None:
        context_names = [(c.context, c.name) for c in cmd]
        existing_components = self.query_service.find_by_context_names(context_names)
        
        existing_dict = {
            (c.context, c.name): c for c in existing_components
        }
        components = ComponentDTOMapper.to_domain_entities(cmd, existing_dict)
        
        with self.uow:
            self.uow.repository.save_all(components)
            self.uow.commit()