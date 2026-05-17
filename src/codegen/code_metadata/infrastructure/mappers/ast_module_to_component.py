import ast
from dataclasses import dataclass
from typing import ClassVar

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)
from codegen.shared.domain.value_objects.snake_string import SnakeString


@dataclass
class AstModuleToComponent:
    _CODEGEN_PREFIX: ClassVar[str] = "codegen."

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
        component_type = self._resolve_component_type(module_path)
        return [
            ImportedComponent(
                context=context,
                name=alias.name,
                type=component_type,
            )
            for alias in node.names
        ]

    def _resolve_context(self, module_path: str) -> str:
        """Strip the ``codegen.`` prefix for internal imports; keep the full path for external ones."""
        if module_path.startswith(self._CODEGEN_PREFIX):
            return module_path.removeprefix(self._CODEGEN_PREFIX).split(".")[0]
        return module_path

    def _resolve_component_type(self, module_path: str) -> str:
        if not module_path.startswith(self._CODEGEN_PREFIX):
            return str(ComponentType.EXTERNAL)
        for ct in ComponentType:
            if ct.dir_name in module_path:
                return str(ct)
        return str(ComponentType.EXTERNAL)
