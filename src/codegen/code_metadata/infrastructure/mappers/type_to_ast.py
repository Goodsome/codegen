import ast
from dataclasses import dataclass
from typing import Self

from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class TypeToAst:
    
    resolver: ReferenceResolver

    @classmethod
    def create(cls, resolver: ReferenceResolver) -> Self:
        return cls(resolver=resolver)

    def map(self, type_: TypeDef | None) -> ast.expr | None:
        if type_ is None:
            return None
        return self.map_type(type_)
        
    def map_type(self, type_: TypeDef) -> ast.expr:
        name = self.resolver.resolve_reference_target(
            type_.origin,
        )
        if name == PythonBuiltinType.NONE:
            return ast.Constant(value=None, kind=None)

        base_node = ast.Name(id=name, ctx=ast.Load())
        if not type_.args:
            return base_node

        if len(type_.args) == 1:
            slice_node = self.map(type_.args[0])
        else:
            slice_node = ast.Tuple(
                elts=[self.map(arg) for arg in type_.args],
                ctx=ast.Load(),
            )

        return ast.Subscript(
            value=base_node,
            slice=slice_node,
            ctx=ast.Load(),
        )