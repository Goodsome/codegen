import ast
from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.code_metadata.infrastructure.mappers.ast_module_to_component import (
    AstModuleToComponent,
)


@dataclass
class PythonCodeParser(CodeParser):
    mapper: AstModuleToComponent

    @override
    def parse(self, code: str, component_name: str) -> ParsedComponent:
        module = ast.parse(code)
        return self.mapper.map(module, component_name=component_name)

    @override
    def parse_dependencies(self, code: str, component_path: Path) -> set[ImportedComponent]:
        module = ast.parse(code)
        return self.mapper.parse_imports(module=module, component_path=component_path)
        