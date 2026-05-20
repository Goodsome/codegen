import ast
from dataclasses import dataclass
from typing import Self

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.infrastructure.mappers.attribute_to_ast_assign import (
    AttributeToAstAssign,
)
from codegen.code_metadata.infrastructure.mappers.type_to_ast import TypeToAst


@dataclass
class ComponentToAstClass:
    component_policy_factory: ComponentPolicyFactory
    attribute_to_ast_assign: AttributeToAstAssign
    type_to_ast: TypeToAst

    @classmethod
    def create(
        cls,
        component_policy_factory: ComponentPolicyFactory,
        resolver: ReferenceResolver,
    ) -> Self:
        return cls(
            component_policy_factory=component_policy_factory,
            attribute_to_ast_assign=AttributeToAstAssign.create(resolver),
            type_to_ast=TypeToAst.create(resolver),
        )

    def map(
        self,
        component: Component,
    ) -> ast.ClassDef:
        body: list[ast.stmt] = []
        if component.description:
            body.append(ast.Expr(value=ast.Constant(value=component.description)))
        for attribute in component.attributes:
            body.append(self.attribute_to_ast_assign.map(attribute))
        if not body:
            body.append(ast.Expr(ast.Constant(value=...)))
        bases = [self.type_to_ast.map_type(t) for t in component.bases]
        class_def = ast.ClassDef(
            name=component.name,
            bases=bases,
            keywords=[],
            body=body,
        )
        return class_def
