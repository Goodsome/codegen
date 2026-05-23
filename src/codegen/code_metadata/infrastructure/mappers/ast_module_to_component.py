import ast
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from codegen.code_metadata.application.dtos.import_dto import ImportDto
from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_attribute import (
    AstNodeToAttribute,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_expr import AstNodeToExpr
from codegen.code_metadata.infrastructure.mappers.ast_node_to_parsed_type import (
    AstNodeToParsedType,
)
from codegen.code_metadata.infrastructure.mappers.ast_to_behavior_mixin import (
    AstToBehaviorMixin,
)


@dataclass
class AstModuleToComponent(
    AstToBehaviorMixin,
    AstClassToComponent,
    AstNodeToParsedType,
    AstNodeToExpr,
    AstNodeToAttribute,
):
    _CODEGEN_PREFIX: ClassVar[str] = "codegen."

    def parse_node_to_behavior(self, node: ast.AST) -> ParsedBehavior:
        match node:
            case ast.FunctionDef():
                return self.function_def_to_behavior(node)
            case _:
                raise ValueError(f"not support {node=}")

    def parse_node_to_attribute(self, node: ast.AST) -> ParsedAttribute:
        match node:
            case ast.AnnAssign():
                return self.ann_assign_to_attribute(node)
            case ast.Assign():
                return self.assign_to_attribute(node)
            case ast.arg():
                return self.arg_to_attribute(node)
            case _:
                raise ValueError(f"not support {node=}")

    def parse_node_to_attributes(self, node: ast.arguments) -> list[ParsedAttribute]:
        return self._parse_node_to_attributes(node)

    def parse_node_to_type(self, node: ast.AST) -> ParsedType:
        return self._node_to_type(node)

    def parse_node_to_expr(self, node: ast.expr) -> ParsedExpr:
        return self._node_to_expr(node)

    def map(self, module: ast.Module, component_name: str) -> ParsedComponent:
        component: ParsedComponent | None = None
        imports: list[ImportDto] = []
        for node in module.body:
            imports.extend(self.try_get_imports(node))
        for node in module.body:
            component = self.try_get_component(node, component_name, imports=imports)
        if component is None:
            raise ValueError(f"No class definition found in module {component_name}")
        return component

    def try_get_component(
        self, node: ast.AST, component_name: str, imports: list[ImportDto],
    ) -> ParsedComponent | None:
        if isinstance(node, ast.ClassDef) and node.name == component_name:
            return self.class_def_to_component(node, imports=imports)
        elif isinstance(node, ast.Assign):
            return self.parse_assign(node, component_name)
        return None

    def try_get_imports(
        self, node: ast.stmt,
    ) -> list[ImportDto]:
        if isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            return [ImportDto(module=module, names=[a.name for a in node.names])]
        elif isinstance(node, ast.Import):
            return [ImportDto(module=a.name, names=[]) for a in node.names]
        elif isinstance(node, ast.If):
            imports: list[ImportDto] = []
            for subnode in node.body:
                imports.extend(self.try_get_imports(subnode))
            for subnode in node.orelse:
                imports.extend(self.try_get_imports(subnode))
            return imports
        return []

    def parse_assign(
        self, node: ast.Assign, component_name: str
    ) -> ParsedComponent | None:
        if len(node.targets) != 1:
            return None
        if not isinstance(node.targets[0], ast.Name):
            return None
        if node.targets[0].id != component_name:
            return None
        parsed_attribute = self.parse_node_to_attribute(node)
        return ParsedComponent(
            name=component_name,
            description="",
            attributes=[parsed_attribute],
            behaviors=[],
            bases=[],
            imports=[],
        )

    def parse_imports(
        self, module: ast.Module, component_path: Path
    ) -> set[ImportedComponent]:
        ics: set[ImportedComponent] = set()
        for node in module.body:
            if isinstance(node, ast.ImportFrom):
                ics.update(self.parse_import(node, component_path))
            elif isinstance(node, ast.If):
                for subnode in node.body:
                    if isinstance(subnode, ast.ImportFrom):
                        ics.update(self.parse_import(subnode, component_path))
        return ics

    def parse_import(
        self, node: ast.ImportFrom, component_path: Path
    ) -> list[ImportedComponent]:
        module_path = node.module
        if module_path is None:
            return []

        if node.level > 0:
            module_path = str(component_path.parent).replace("/", ".")
            if module_path.startswith("src."):
                module_path = module_path.removeprefix("src.")

        context = self._resolve_context(module_path)
        return [
            ImportedComponent(
                context=context,
                name=alias.name,
                import_module=module_path
            )
            for alias in node.names
        ]

    def _resolve_context(self, module_path: str) -> str:
        """Strip the ``codegen.`` prefix for internal imports; keep the full path for external ones."""
        if module_path.startswith(self._CODEGEN_PREFIX):
            return module_path.removeprefix(self._CODEGEN_PREFIX).split(".")[0]
        return module_path
