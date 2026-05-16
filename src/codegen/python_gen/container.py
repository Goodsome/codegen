from codegen.python_gen.application.services.parse_code import ParseCode
from codegen.python_gen.application.use_cases.generate_package import GeneratePackage
from codegen.python_gen.application.use_cases.generate_schema_json import GenerateSchemaJson
from codegen.python_gen.application.use_cases.parse_package import ParsePackage
from codegen.python_gen.domain.services.python_syntax_translator import (
    PythonSyntaxTranslator,
)
from codegen.python_gen.infrastructure.adapters.ast_translator import AstTranslator
from codegen.python_gen.infrastructure.adapters.black_code_formatter import (
    BlackCodeFormatter,
)
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Singleton

from codegen.shared.domain.ports.file_system_port import FileSystemPort


class Container(DeclarativeContainer):
    file_system_port: Dependency[FileSystemPort] = Dependency(instance_of=FileSystemPort)

    ast_translator: Singleton[AstTranslator] = Singleton(AstTranslator)

    code_formatter: Singleton[BlackCodeFormatter] = Singleton(BlackCodeFormatter)

    python_syntax_translator: Singleton[PythonSyntaxTranslator] = Singleton(
        PythonSyntaxTranslator,
        source_code_port=ast_translator,
        file_system_port=file_system_port,
    )

    parse_package: Factory[ParsePackage] = Factory(ParsePackage, translator=python_syntax_translator)

    generate_schema_json: Factory[GenerateSchemaJson] = Factory(
        GenerateSchemaJson,
        file_system_port=file_system_port,
    )

    generate_package: Factory[GeneratePackage] = Factory(
        GeneratePackage,
        file_system_port=file_system_port,
        translator=python_syntax_translator,
        code_formatter=code_formatter,
    )

    parse_code: Factory[ParseCode] = Factory(
        ParseCode,
        source_code_port=ast_translator,
        file_system_port=file_system_port,
    )

    