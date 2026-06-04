import ast
from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.ports.code_parser import CodeParser
from codegen.code_metadata.domain.value_objects import AstStmt
from codegen.code_metadata.infrastructure.mappers.ast_to_stmt import AstToStmt
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class ASTCodeParser(CodeParser):
    file_system: FileSystemPort

    @override
    def parse_file(self, path: Path) -> CodeDocument:
        code = self.file_system.read_file(path)
        return CodeDocument(physical_path=path, body=self._parse_code(code))

    @override
    def parse_directory(self, path: Path) -> list[CodeDocument]:
        files = self.file_system.list_directory_recursively(path, pattern="*.py")
        return [self.parse_file(file) for file in files]

    def _parse_code(self, code: str) -> list[AstStmt]:
        ast_module = ast.parse(code)
        return [AstToStmt.to_stmt(node) for node in ast_module.body]
