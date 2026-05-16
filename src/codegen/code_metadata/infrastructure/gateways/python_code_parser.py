from pathlib import Path
from typing import override

from dataclasses import dataclass
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.python_gen.application.services.parse_code import ParseCode
from codegen.code_metadata.infrastructure.mappers.module_to_parsed_component import ModuleToParsedComponent


@dataclass
class PythonCodeParser(CodeParser):

    module_parser: ParseCode
    mapper: ModuleToParsedComponent

    @override
    def parse(self, code_path: Path) -> ParsedComponent:
        module = self.module_parser.execute(code_path)
        parsed_component = self.mapper.execute(module)
        return parsed_component