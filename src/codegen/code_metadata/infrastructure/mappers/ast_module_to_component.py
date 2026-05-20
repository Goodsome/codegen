import ast
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)


@dataclass
class AstModuleToComponent:
    _CODEGEN_PREFIX: ClassVar[str] = "codegen."

    ast_class_to_component: AstClassToComponent

    def map(self, module: ast.Module, component_name: str) -> ParsedComponent:
        component: ParsedComponent | None = None
        for node in module.body:
            component = self.try_get_component(node, component_name)
        if component is None:
            raise ValueError(f"No class definition found in module {component_name}")
        return component

    def try_get_component(self, node: ast.AST, component_name: str) -> ParsedComponent | None:
        if isinstance(node, ast.ClassDef) and node.name == component_name:
            return self.ast_class_to_component.map(node)
        elif isinstance(node, ast.Assign):
            return self.parse_assign(node, component_name)
        return None
        
    def parse_assign(self, node: ast.Assign, component_name: str) -> ParsedComponent | None:
        if len(node.targets) != 1:
            return None
        if not isinstance(node.targets[0], ast.Name):
            return None
        if node.targets[0].id != component_name:
            return None
        parsed_attribute = self.ast_class_to_component.ast_node_to_attribute.map(node)
        if parsed_attribute is None:
            return None
        return ParsedComponent(
            name=component_name,
            description="",
            attributes=[parsed_attribute]
        )

    def parse_imports(self, module: ast.Module, component_path: Path) -> set[ImportedComponent]:
        ics: set[ImportedComponent] = set()
        for node in module.body:
            if isinstance(node, ast.ImportFrom):
                ics.update(self.parse_import(node, component_path))
            elif isinstance(node, ast.If):
                for subnode in node.body:
                    if isinstance(subnode, ast.ImportFrom):
                        ics.update(self.parse_import(subnode, component_path))
        return ics

    def parse_import(self, node: ast.ImportFrom, component_path: Path) -> list[ImportedComponent]:
        module_path = node.module
        if module_path is None:
            return []

        if node.level > 0:
            module_path = str(component_path.parent).replace("/", ".")
            if module_path.startswith("src."):
                module_path = module_path.removeprefix("src.")
            
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
