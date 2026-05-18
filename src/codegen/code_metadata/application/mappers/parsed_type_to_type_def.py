from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.type_def import TypeDef


@dataclass
class ParsedTypeToTypeDef:
    
    def map(self, parsed_type: ParsedType, dependencies: dict[str, ComponentId]) -> TypeDef:
        origin = parsed_type.origin
        if origin is None:
            assert parsed_type.component_name is not None, parsed_type
            if parsed_type.component_name not in dependencies:
                raise ValueError(f"Component `{parsed_type.component_name}` not found in dependencies, maybe is PythonBuiltinType")
            origin = dependencies[parsed_type.component_name]
        args = tuple(self.map(arg, dependencies) for arg in parsed_type.args)
        return TypeDef(
            origin=origin,
            args=args
        )
