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
        ics: list[ImportedComponent] = []
        component: ParsedComponent | None = None
        for node in module.body:
            if isinstance(node, ast.ClassDef) and SnakeString(node.name) == module_name:
                component = self.ast_class_to_component.map(node)
            elif isinstance(node, ast.ImportFrom):
                ics.extend(self.parse_import(node))
        if component is None:
            raise ValueError(f"No class definition found in module {module_name}")
        component.imported_components = ics
        return component

    def parse_import(self, node: ast.ImportFrom) -> list[ImportedComponent]:
        module_path = node.module
        if module_path is None:
            return []

        context = self._resolve_context(module_path)
        return [
            ImportedComponent(context=context, component=alias.name)
            for alias in node.names
        ]

    @staticmethod
    def _resolve_context(module_path: str) -> str:
        """Strip the ``codegen.`` prefix for internal imports; keep the full path for external ones."""
        _CODEGEN_PREFIX = "codegen."
        if module_path.startswith(_CODEGEN_PREFIX):
            return module_path.removeprefix(_CODEGEN_PREFIX)
        return module_path
