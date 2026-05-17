import ast
from dataclasses import dataclass
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.factories.component_policy_factory import ComponentPolicyFactory


@dataclass
class ComponentToAstClass:

    component_policy_factory: ComponentPolicyFactory

    def map(self, component: Component) -> ast.ClassDef:
        body: list[ast.stmt] = []
        body.append(ast.Expr(value=ast.Constant(value=component.description)))
        class_def = ast.ClassDef(
            name=component.name,
            bases=[],
            keywords=[],
            body=body,
        )
        return class_def
