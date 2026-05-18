from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.mappers.parsed_type_to_type_def import (
    ParsedTypeToTypeDef,
)
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)


@dataclass
class ParsedAttributeMapper:
    parsed_type_to_type_def: ParsedTypeToTypeDef

    def to_attribute_sync_data(
        self,
        parsed_attribute: ParsedAttribute,
        dependencies: dict[str, ComponentId],
    ) -> AttributeSyncData:
        type_def = self.parsed_type_to_type_def.map(parsed_attribute.type, dependencies)
        return AttributeSyncData(
            name=parsed_attribute.name,
            type=type_def,
        )
