import ast
from dataclasses import dataclass
from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.factories.component_policy_factory import ComponentPolicyFactory
from codegen.code_metadata.domain.identifiers.component_id import ComponentId


@dataclass
class ComponentToAstClass:

    component_policy_factory: ComponentPolicyFactory

    def map(self, component: Component, dep_components: dict[ComponentId, ComponentDTO]) -> ast.ClassDef:
        body: list[ast.stmt] = []
        body.append(ast.Expr(value=ast.Constant(value=component.description)))
        bases = [t.to_ast_node(components=dep_components) for t in component.bases]
        class_def = ast.ClassDef(
            name=component.name,
            bases=bases,
            keywords=[],
            body=body,
        )
        return class_def
