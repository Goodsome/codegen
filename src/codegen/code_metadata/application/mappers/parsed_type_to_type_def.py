from dataclasses import dataclass
from typing import Self, overload

from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.type_def import TypeDef


@dataclass
class ParsedTypeToTypeDef:
    resolver: ReferenceResolver

    @classmethod
    def create(cls, resolver: ReferenceResolver) -> Self:
        return cls(resolver=resolver)

    @overload
    def map_type(self, parsed_type: None) -> None:...
    
    @overload
    def map_type(self, parsed_type: ParsedType) -> TypeDef:...
    
    def map_type(
        self, parsed_type: ParsedType | None
    ) -> TypeDef | None:
        if parsed_type is None:
            return None
        origin = self.resolver.resolve_target(parsed_type.origin)
        args = tuple(self.map_type(arg) for arg in parsed_type.args)
        return TypeDef(origin=origin, args=args)
