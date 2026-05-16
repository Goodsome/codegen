import ast
from dataclasses import dataclass
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.infrastructure.mappers.component_to_ast_class import ComponentToAstClass


@dataclass
class ComponentToAstModule:

    component_to_ast_class: ComponentToAstClass

    def map(self, component: Component) -> ast.Module:
        body: list[ast.stmt] = []
        body.append(self.component_to_ast_class.map(component))
        module = ast.Module(
            body=body,
        )
        return module