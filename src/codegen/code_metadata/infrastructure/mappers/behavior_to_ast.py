import ast
from dataclasses import dataclass
from typing import Self
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.infrastructure.mappers.attribute_to_ast_assign import AttributeToAstAssign
from codegen.code_metadata.infrastructure.mappers.type_to_ast import TypeToAst


@dataclass
class BehaviorToAst:

    attribute_to_ast: AttributeToAstAssign
    type_to_ast: TypeToAst

    @classmethod
    def create(
        cls,
        resolver: ReferenceResolver,
    ) -> Self:
        return cls(
            attribute_to_ast=AttributeToAstAssign.create(resolver),
            type_to_ast=TypeToAst.create(resolver),
        )
    
    def to_ast(self, behavior: Behavior) -> ast.FunctionDef:
        body: list[ast.stmt] = []
        if behavior.description:
            body.append(ast.Expr(value=ast.Constant(value=behavior.description)))
        body.append(
            ast.Expr(value=ast.Constant(value=...))
        )
        arguments = self.attribute_to_ast.attributes_to_arguments(behavior.inputs)
        returns = self.type_to_ast.map(behavior.output)
        return ast.FunctionDef(
            name=behavior.name,
            args=arguments,
            body=body,
            returns=returns,
        )