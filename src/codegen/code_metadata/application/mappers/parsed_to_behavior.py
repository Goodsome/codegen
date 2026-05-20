from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.mappers import parsed_type_to_type_def
from codegen.code_metadata.application.mappers.parsed_attribute_mapper import ParsedAttributeMapper
from codegen.code_metadata.application.mappers.parsed_type_to_type_def import ParsedTypeToTypeDef
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.behavior_sync_data import BehaviorSyncData


@dataclass
class ParsedToBehavior:

    attribute_mapper: ParsedAttributeMapper
    parsed_type_to_type_def: ParsedTypeToTypeDef

    @classmethod
    def create(cls, resolver: ReferenceResolver):
        return cls(
            attribute_mapper=ParsedAttributeMapper.create(resolver),
            parsed_type_to_type_def=ParsedTypeToTypeDef.create(resolver)
        )

    def to_behavior(self, parsed_behavior: ParsedBehavior) -> BehaviorSyncData:
        inputs = [self.attribute_mapper.to_attribute_sync_data(a) for a in parsed_behavior.inputs]
        output = self.parsed_type_to_type_def.map_type(parsed_behavior.output)
        return BehaviorSyncData(
            name=parsed_behavior.name,
            description=parsed_behavior.description or "",
            inputs=inputs,
            output=output,
        )