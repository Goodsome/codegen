from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.application.dtos.create_component_command import (
    CreateComponentCommand,
)
from codegen.code_metadata.application.dtos.upsert_component_command import UpsertComponentCommand
from codegen.code_metadata.domain.identifiers.component_id import ComponentId

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType


class ComponentMapper:
    @classmethod
    def to_domain(
        cls,
        dto: CreateComponentCommand | UpsertComponentCommand,
        existing_component: ComponentDTO | None = None,
    ) -> Component:

        if existing_component:
            component_id = ComponentId.reconstitute(existing_component.id)
        else:
            component_id = ComponentId.create()

        return Component(
            id=component_id,
            type=ComponentType(dto.type),
            name=dto.name,
            description=dto.description,
            context=dto.context,
        )
