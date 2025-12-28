from dataclasses import dataclass
from pathlib import Path
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.services.python_syntax_translator import (
    PythonSyntaxTranslator,
)


@dataclass(frozen=True)
class ParsePackageQuery:

    package_path: Path


@dataclass(frozen=True)
class ParsePackageResult:

    package_spec: PackageSpec


@dataclass
class ParsePackage:
    """Parses Python package to PackageSpec."""

    translator: PythonSyntaxTranslator

    def execute(self, query: ParsePackageQuery) -> ParsePackageResult:
        spec = self.translator.to_package_spec(query.package_path)
        return ParsePackageResult(package_spec=spec)
