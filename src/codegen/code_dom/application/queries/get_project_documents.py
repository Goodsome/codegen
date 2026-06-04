from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.ports.code_parser import CodeParser


class GetProjectDocumentsQuery(BaseModel):
    dir_path: Path


class GetProjectDocumentsResult(BaseModel):
    code_documents: list[CodeDocument]


@dataclass
class GetProjectDocumentsHandler:
    code_parser: CodeParser

    def handle(self, query: GetProjectDocumentsQuery) -> GetProjectDocumentsResult:
        code_document = self.code_parser.parse_directory(query.dir_path)

        return GetProjectDocumentsResult(code_documents=code_document)
