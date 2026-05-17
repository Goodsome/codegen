import ast
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.infrastructure.mappers.component_to_ast_class import (
    ComponentToAstClass,
)


@dataclass
class ComponentToAstModule:
    component_to_ast_class: ComponentToAstClass

    def map(
        self, component: Component, dep_components: dict[ComponentId, ComponentDTO]
    ) -> ast.Module:
        body: list[ast.stmt] = [
            self.component_to_ast_class.map(component, dep_components=dep_components)
        ]
        module = ast.Module(
            body=body,
        )
        return module
