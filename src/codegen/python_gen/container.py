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
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory, Singleton


class Container(DeclarativeContainer):
    file_system_port = Dependency()

    ast_translator = Singleton(AstTranslator)

    code_formatter = Singleton(BlackCodeFormatter)

    python_syntax_translator = Singleton(
        PythonSyntaxTranslator,
        source_code_port=ast_translator,
        file_system_port=file_system_port,
    )

    parse_package = Factory(ParsePackage, translator=python_syntax_translator)

    generate_schema_json = Factory(
        GenerateSchemaJson,
        file_system_port=file_system_port,
    )

    generate_package = Factory(
        GeneratePackage,
        file_system_port=file_system_port,
        translator=python_syntax_translator,
        code_formatter=code_formatter,
    )
