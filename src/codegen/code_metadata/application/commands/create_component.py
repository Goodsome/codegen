from dataclasses import dataclass

from codegen.code_metadata.application.dtos.create_component_command import CreateComponentCommand
from codegen.code_metadata.application.dtos.create_component_result import CreateComponentResult
from codegen.code_metadata.application.mappers.component_mapper import ComponentMapper
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork



@dataclass
class CreateComponent:
    uow: UnitOfWork[ComponentRepository]

    def execute(self, cmd: CreateComponentCommand) -> CreateComponentResult:
        component = ComponentMapper.to_domain(cmd)
        
        with self.uow:
            self.uow.repository.add(component)
            self.uow.commit()
            
        return CreateComponentResult(component_id=str(component.id))