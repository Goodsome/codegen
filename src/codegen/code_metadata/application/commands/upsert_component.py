import logging

from dataclasses import dataclass

from codegen.code_metadata.application.dtos.upsert_component_command import UpsertComponentCommand
from codegen.code_metadata.application.dtos.upsert_component_result import UpsertComponentResult
from codegen.code_metadata.application.ports.component_query_service import ComponentQueryService
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.code_metadata.application.mappers.component_mapper import ComponentMapper

logger = logging.getLogger(__name__)

@dataclass
class UpsertComponent:
    uow: UnitOfWork[ComponentRepository]
    query_service: ComponentQueryService

    def execute(self, cmd: UpsertComponentCommand) -> UpsertComponentResult:

        logger.info(f"Upserting component: name={cmd.name}, context={cmd.context}, type={cmd.type}")
        
        dto = self.query_service.find_by_name(
            name=cmd.name,
            context=cmd.context
        )
        component = ComponentMapper.to_domain(
            dto=cmd, 
            existing_component=dto
        )
        
        with self.uow:
            self.uow.repository.save(component)
            self.uow.commit()
            
        return UpsertComponentResult(component_id=str(component.id))
