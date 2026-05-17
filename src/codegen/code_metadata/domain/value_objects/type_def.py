import ast
from typing import Self

from pydantic import Field

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
