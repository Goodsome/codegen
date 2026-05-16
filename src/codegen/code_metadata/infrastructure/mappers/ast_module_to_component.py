import ast
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)


@dataclass
class AstModuleToComponent:
    ast_class_to_component: AstClassToComponent

    def map(self, module: ast.Module) -> ParsedComponent:
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                return self.ast_class_to_component.map(node)
        raise ValueError("No class definition found in module")
