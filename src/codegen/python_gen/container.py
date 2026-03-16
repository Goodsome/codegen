from codegen.python_gen.application.use_cases.parse_package import ParsePackage
from codegen.python_gen.infrastructure.adapters.black_code_formatter import (
    BlackCodeFormatter,
)
from dependency_injector.providers import Factory
from codegen.python_gen.application.use_cases.generate_schema_json import (
    GenerateSchemaJson,
)
from dependency_injector.containers import DeclarativeContainer
from codegen.python_gen.infrastructure.adapters.ast_translator import AstTranslator
from codegen.python_gen.application.use_cases.generate_package import GeneratePackage


class Container(DeclarativeContainer):
    ast_translator = Factory(AstTranslator)
    black_code_formatter = Factory(BlackCodeFormatter)
    parse_package = Factory(ParsePackage)
    generate_schema_json = Factory(GenerateSchemaJson)
    generate_package = Factory(GeneratePackage, code_formatter=black_code_formatter)
