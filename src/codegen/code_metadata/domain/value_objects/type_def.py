import ast
from typing import Self

from pydantic import Field

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.value_object import ValueObject
from codegen.shared.domain.enums import ContainerType, PrimitiveType, PythonBuiltinType


class TypeDef(ValueObject):
    origin: PrimitiveType | ContainerType | PythonBuiltinType | ComponentId
    args: tuple[Self, ...] = Field(default_factory=tuple)

    @classmethod
    def parse_code(cls, code: str, components: dict[str, ComponentId]) -> Self:
        ast_tree = ast.parse(code)
        if len(ast_tree.body) != 1:
            raise ValueError(
                f"Expected 1 AST node, got {len(ast_tree.body)}, code: {code}"
            )
        node = ast_tree.body[0]
        return cls.parse_ast_node(node, components)

    @classmethod
    def parse_ast_node(cls, node: ast.AST, components: dict[str, ComponentId]) -> Self:
        if isinstance(node, ast.Expr):
            return cls.parse_ast_expr(node, components)
        elif isinstance(node, ast.Name):
            return cls.parse_ast_name(node, components)
        elif isinstance(node, ast.Subscript):
            return cls.parse_ast_subscript(node, components)
        raise NotImplementedError(f"Unsupported AST node: {node}")

    @classmethod
    def parse_ast_expr(cls, expr: ast.Expr, components: dict[str, ComponentId]) -> Self:
        return cls.parse_ast_node(expr.value, components)

    @classmethod
    def parse_ast_subscript(
        cls, expr: ast.Subscript, components: dict[str, ComponentId]
    ) -> Self:
        container = cls.parse_ast_node(expr.value, components)
        args: tuple[Self, ...]
        if isinstance(expr.slice, ast.Tuple):
            args = tuple(
                cls.parse_ast_node(slice, components) for slice in expr.slice.elts
            )
        else:
            args = (cls.parse_ast_node(expr.slice, components),)

        return cls(origin=container.origin, args=args)

    @classmethod
    def parse_ast_name(cls, expr: ast.Name, components: dict[str, ComponentId]) -> Self:
        name = expr.id
        if name in PrimitiveType._value2member_map_:
            return cls(origin=PrimitiveType(name))
        elif name in ContainerType._value2member_map_:
            return cls(origin=ContainerType(name))
        elif name in PythonBuiltinType._value2member_map_:
            _t = PythonBuiltinType(name)
            return cls(origin=_t.to_primitive_type() or _t)
        elif name in components:
            return cls(origin=components[name])

        raise ValueError(f"Unknown component: {name}")

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        if isinstance(self.origin, ComponentId):
            result.add(self.origin)
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