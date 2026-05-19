import ast
from dataclasses import dataclass
from typing import Self

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.infrastructure.mappers.expr_to_ast import ExprToAst


@dataclass
class AttributeToAstAssign:
    expr_to_ast: ExprToAst

    @classmethod
    def create(cls, resolver: ReferenceResolver) -> Self:
        return cls(expr_to_ast=ExprToAst.create(resolver))

    def map(
        self, attribute: Attribute, dependencies: dict[ComponentId, ComponentDTO]
    ) -> ast.AnnAssign | ast.Assign | ast.Expr:
        target = ast.Name(id=attribute.name, ctx=ast.Store())
        if attribute.type is not None:
            annotation = attribute.type.to_ast_node(components=dependencies)
        else:
            annotation = None

        value = self.expr_to_ast.map(attribute.value)

        if annotation:
            return ast.AnnAssign(
                target=target,
                annotation=annotation,
                value=value,
                simple=1,
            )
        elif value is not None:
            return ast.Assign(
                targets=[target],
                value=value,
            )
        else:
            return ast.Expr(
                value=ast.Name(id=attribute.name, ctx=ast.Load()),
            )
