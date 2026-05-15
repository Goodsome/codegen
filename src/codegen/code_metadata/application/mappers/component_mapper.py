from codegen.code_metadata.application.dtos.create_component_command import CreateComponentCommand
from codegen.code_metadata.domain.identifiers.component_id import ComponentId

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType


class ComponentMapper():

    @classmethod
    def to_domain(cls, dto: CreateComponentCommand) -> Component:
        
        return Component(
            id=ComponentId.create(),
            type=ComponentType(dto.type),
            name=dto.name,
            description=dto.description,
            context=dto.context,
        )
    