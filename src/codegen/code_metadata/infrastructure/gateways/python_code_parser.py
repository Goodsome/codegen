import ast
from dataclasses import dataclass
from typing import override

from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.code_metadata.infrastructure.mappers.ast_module_to_component import (
    AstModuleToComponent,
)


@dataclass
class PythonCodeParser(CodeParser):
    mapper: AstModuleToComponent

    @override
    def parse(self, code: str) -> ParsedComponent:
        module = ast.parse(code)
        return self.mapper.map(module)
