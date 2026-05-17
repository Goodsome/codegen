import ast
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)
from codegen.shared.domain.value_objects.snake_string import SnakeString


@dataclass
class AstModuleToComponent:
    ast_class_to_component: AstClassToComponent

    def map(self, module: ast.Module, module_name: str) -> ParsedComponent:
        ics = self._parse_imports(module)
        for node in module.body:
            if isinstance(node, ast.ClassDef) and SnakeString(node.name) == module_name:
                component = self.ast_class_to_component.map(node)
                component.imported_components = ics
                return component
        raise ValueError(f"No class definition found in module {module_name}")

    def _parse_imports(self, module: ast.Module) -> list[ImportedComponent]:
        return []
        
