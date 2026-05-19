from typing import Self
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.mappers.parsed_expr_to_def import ParsedExprToDef
from codegen.code_metadata.application.mappers.parsed_type_to_type_def import (
    ParsedTypeToTypeDef,
)
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.attribute_sync_data import (
    AttributeSyncData,
)


@dataclass
class ParsedAttributeMapper:
    parsed_type_to_type_def: ParsedTypeToTypeDef
    parsed_expr_to_def: ParsedExprToDef

    @classmethod
    def create(
        cls,
        resolver: ReferenceResolver,
    ) -> Self:
        return cls(
            parsed_type_to_type_def=ParsedTypeToTypeDef.create(resolver=resolver),
            parsed_expr_to_def=ParsedExprToDef.create(resolver=resolver),
        )

    def to_attribute_sync_data(
        self,
        parsed_attribute: ParsedAttribute,
        dependencies: dict[str, ComponentId],
    ) -> AttributeSyncData:
        type_def = self.parsed_type_to_type_def.map(parsed_attribute.type, dependencies)
        expr_def = self.parsed_expr_to_def.map(parsed_attribute.value)
        return AttributeSyncData(
            name=parsed_attribute.name,
            type=type_def,
            value=expr_def,
        )
