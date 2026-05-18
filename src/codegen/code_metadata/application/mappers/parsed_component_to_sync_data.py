from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.mappers.parsed_attribute_mapper import ParsedAttributeMapper
from codegen.code_metadata.application.mappers.parsed_type_to_type_def import (
    ParsedTypeToTypeDef,
)
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.component_sync_data import (
    ComponentSyncData,
)


@dataclass
class ParsedComponentToSyncData:
    parsed_type_to_type_def: ParsedTypeToTypeDef
    parsed_attribute_mapper: ParsedAttributeMapper

    def map(
        self,
        context: str,
        parsed_component: ParsedComponent,
        component_type: ComponentType,
        dependencies: dict[str, ComponentId],
    ) -> ComponentSyncData:
        bases = [
            self.parsed_type_to_type_def.map(base, dependencies)
            for base in parsed_component.bases
        ]
        attributes = [
            self.parsed_attribute_mapper.to_attribute_sync_data(attr, dependencies)
            for attr in parsed_component.attributes
        ]
        return ComponentSyncData(
            context=context,
            name=parsed_component.name,
            type=component_type,
            description=parsed_component.description,
            bases=bases,
            attributes=attributes,
        )
