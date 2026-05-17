from calendar import c

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.application.dtos.upsert_component_command import (
    UpsertComponentCommand,
)
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.type_def import TypeDef


class ComponentDTOMapper:
    @classmethod
    def to_domain(
        cls,
        dto: UpsertComponentCommand,
        existing_component: ComponentDTO | None = None,
        components_map: dict[str, ComponentId] | None = None,
    ) -> Component:
        if components_map is None:
            components_map = {}
        
        if existing_component:
            component_id = ComponentId.reconstitute(existing_component.id)
        else:
            component_id = ComponentId.create()

        bases = [TypeDef.parse_code(b, components_map) for b in dto.bases]

        return Component(
            id=component_id,
            type=ComponentType(dto.type),
            name=dto.name,
            description=dto.description,
            context=dto.context,
            bases=bases,
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
            components_map = {
                ec.name: ComponentId.reconstitute(ec.id)
                for ec in existing_components.values()
            }
            entities.append(cls.to_domain(dto, existing_component, components_map))
        return entities
