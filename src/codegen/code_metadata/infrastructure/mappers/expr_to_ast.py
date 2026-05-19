import ast
from dataclasses import dataclass
from typing import Self

from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.call_expr import CallExpr
from codegen.code_metadata.domain.value_objects.constant_expr import ConstantExpr
from codegen.code_metadata.domain.value_objects.dict_expr import DictExpr
from codegen.code_metadata.domain.value_objects.expr_def import ExprDef
from codegen.code_metadata.domain.value_objects.reference_expr import ReferenceExpr
from codegen.code_metadata.domain.value_objects.sequence_expr import SequenceExpr


@dataclass
class ExprToAst:
    resolver: ReferenceResolver

    @classmethod
    def create(cls, resolver: ReferenceResolver) -> Self:
        return cls(resolver=resolver)

    def map(
        self,
        expr: ExprDef | None,
    ) -> ast.expr | None:
        if expr is None:
            return None
        return self.map_expr(expr)

    def map_expr(
        self,
        expr: ExprDef,
    ) -> ast.expr:
        match expr.kind:
            case ExprKind.CONSTANT:
                return self.map_constant(expr)
            case ExprKind.REFERENCE:
                return self.map_reference(expr)
            case ExprKind.CALL:
                return self.map_call(expr)
            case ExprKind.DICT:
                return self.map_dict(expr)
            case ExprKind.SEQUENCE:
                return self.map_sequence(expr)
            case _:
                raise ValueError(f"Unsupported expression kind: {expr.kind}")

    def map_constant(self, expr: ConstantExpr) -> ast.Constant:
        return ast.Constant(value=expr.value)

    def map_reference(
        self,
        expr: ReferenceExpr,
    ) -> ast.Name | ast.Attribute:
        if expr.source is None:
            name = self.resolver.resolve_reference_target(expr.target, None)
            return ast.Name(id=name)
        else:
            source_expr = self.map_expr(expr.source)
            if not isinstance(expr.source, ReferenceExpr):
                raise ValueError("Expected source expression to be an attribute")
            name = self.resolver.resolve_reference_target(
                target=expr.target,
                source_target=expr.source.target,
            )
            return ast.Attribute(value=source_expr, attr=name)

    def map_call(
        self,
        expr: CallExpr,
    ) -> ast.Call:
        func = self.map_expr(expr.callee)
        args = [self.map_expr(arg) for arg in expr.args]
        keywords: list[ast.keyword] = []
        for k, v in expr.kwargs.items():
            if k == "**":
                arg = None
            else:
                arg = k
            keywords.append(ast.keyword(arg=arg, value=self.map_expr(v)))
        return ast.Call(func=func, args=args, keywords=keywords)

    def map_sequence(
        self,
        expr: SequenceExpr,
    ) -> ast.List | ast.Tuple | ast.Set:
        elts = [self.map_expr(elt) for elt in expr.elements]
        ast_container = {"list": ast.List, "tuple": ast.Tuple, "set": ast.Set}[
            expr.container_type
        ]
        return ast_container(elts=elts)

    def map_dict(
        self,
        expr: DictExpr,
    ) -> ast.Dict:
        keys: list[ast.expr | None] = []
        values: list[ast.expr] = []
        for item in expr.items:
            keys.append(self.map_expr(item.key) if item.key is not None else None)
            values.append(self.map_expr(item.value))
        return ast.Dict(keys=keys, values=values)
