from dataclasses import dataclass
from codegen.python_gen.domain.services.python_syntax_translator import (
    PythonSyntaxTranslator,
)
from codegen.python_gen.application.dtos.parse_package_query import ParsePackageQuery
from codegen.python_gen.application.dtos.parse_package_result import ParsePackageResult
from typing import Self


@dataclass
class ParsePackage:
    """Parses Python package to PackageSpec."""

    translator: PythonSyntaxTranslator

    def execute(self: Self, query: ParsePackageQuery) -> ParsePackageResult:
        spec = self.translator.to_package_spec(query.package_path)
        return ParsePackageResult(package_spec=spec)
