from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.application.dtos.upsert_component_command import UpsertComponentCommand
from codegen.code_metadata.domain.identifiers.component_id import ComponentId

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType


class ComponentDTOMapper:
    
    @classmethod
    def to_domain(
        cls,
        dto: UpsertComponentCommand,
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

    @classmethod
    def to_domain_entities(
        cls,
        dtos: list[UpsertComponentCommand],
        existing_components: dict[tuple[str, str], ComponentDTO],
    ) -> list[Component]:
        entities: list[Component] = []
        for dto in dtos:
            existing_component = existing_components.get((dto.context, dto.name))
            entities.append(cls.to_domain(dto, existing_component))
        return entities