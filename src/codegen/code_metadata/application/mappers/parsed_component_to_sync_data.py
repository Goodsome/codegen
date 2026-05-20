from typing import Self
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.mappers.parsed_attribute_mapper import ParsedAttributeMapper
from codegen.code_metadata.application.mappers.parsed_to_behavior import ParsedToBehavior
from codegen.code_metadata.application.mappers.parsed_type_to_type_def import (
    ParsedTypeToTypeDef,
)
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.component_sync_data import (
    ComponentSyncData,
)


@dataclass
class ParsedComponentToSyncData:
    parsed_type_to_type_def: ParsedTypeToTypeDef
    parsed_attribute_mapper: ParsedAttributeMapper
    behavior_mapper: ParsedToBehavior

    @classmethod
    def create(cls, resolver: ReferenceResolver) -> Self:
        return cls(
            parsed_type_to_type_def=ParsedTypeToTypeDef.create(resolver),
            parsed_attribute_mapper=ParsedAttributeMapper.create(resolver),
            behavior_mapper=ParsedToBehavior.create(resolver)
        )

    def map(
        self,
        context: str,
        parsed_component: ParsedComponent,
        component_type: ComponentType,
    ) -> ComponentSyncData:
        bases = [
            self.parsed_type_to_type_def.map_type(base)
            for base in parsed_component.bases
        ]
        attributes = [
            self.parsed_attribute_mapper.to_attribute_sync_data(attr)
            for attr in parsed_component.attributes
        ]
        behaviors = [
            self.behavior_mapper.to_behavior(b)
            for b in parsed_component.behaviors
        ]
        return ComponentSyncData(
            context=context,
            name=parsed_component.name,
            type=component_type,
            description=parsed_component.description,
            bases=bases,
            attributes=attributes,
            behaviors=behaviors
        )
