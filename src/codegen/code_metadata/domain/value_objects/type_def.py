import ast
from typing import Self

from pydantic import Field

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.core.value_object import ValueObject
from codegen.shared.domain.enums import PrimitiveType


class TypeDef(ValueObject):
    origin: ReferenceTarget
    args: tuple[Self, ...] = Field(default_factory=tuple)

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        if self.origin.component_id:
            result.add(self.origin.component_id)
        for arg in self.args:
            result.update(arg.get_component_ids())
        return result

    def to_ast_node(self, components: dict[ComponentId, ComponentDTO]) -> ast.expr:
        """直接构建并返回精准的 AST 类型节点（去除 ast.Expr 包裹）"""
        # 1. 获取当前节点的名称字符串
        if isinstance(self.origin, ComponentId):
            name_str = components[self.origin].name
        elif isinstance(self.origin, PrimitiveType):
            name_str = str(self.origin.to_python_builtin() or self.origin)
        else:
            name_str = str(self.origin)
    
        if name_str == "None":
            return ast.Constant(value=None)
    
        base_node = ast.Name(id=name_str, ctx=ast.Load())
        if not self.args:
            return base_node
    
        if len(self.args) == 1:
            slice_node = self.args[0].to_ast_node(components)
        else:
            slice_node = ast.Tuple(
                elts=[arg.to_ast_node(components) for arg in self.args],
                ctx=ast.Load()
            )
    
        return ast.Subscript(
            value=base_node,
            slice=slice_node,
            ctx=ast.Load()
        )