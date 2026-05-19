from typing import Self
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.type_def import TypeDef


@dataclass
class ParsedTypeToTypeDef:
    resolver: ReferenceResolver

    @classmethod
    def create(cls, resolver: ReferenceResolver) -> Self:
        return cls(
            resolver=resolver
        )
    
    def map(self, parsed_type: ParsedType | None, dependencies: dict[str, ComponentId]) -> TypeDef | None:
        if parsed_type is None:
            return None
        return self.map_type(parsed_type, dependencies)
        
    def map_type(self, parsed_type: ParsedType, dependencies: dict[str, ComponentId]) -> TypeDef:
        origin = self.resolver.resolve_target(parsed_type.origin)
        args = tuple(self.map_type(arg, dependencies) for arg in parsed_type.args)
        return TypeDef(
            origin=origin,
            args=args
        )
