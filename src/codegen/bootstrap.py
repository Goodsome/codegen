from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Factory

from codegen.domain_definition.application.use_cases.load_blueprint import LoadBlueprint
from codegen.domain_definition.application.use_cases.path_operations import (
    GetValue,
    SetValue,
    RemoveValue,
)
from codegen.domain_definition.domain.services.blueprint_path_operations import (
    BlueprintPathOperations,
)
from codegen.domain_definition.domain.services.blueprint_path_resolver import (
    BlueprintPathResolver,
)
from codegen.domain_definition.infrastructure.adapters.yaml_blueprint_storage import (
    YamlBlueprintStorage,
)
from codegen.orchestration.application.use_cases.generate_blueprint import GenerateBlueprint
from codegen.orchestration.application.use_cases.generate_project import GenerateProject
from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackage,
)
from codegen.python_gen.application.use_cases.parse_package import (
    ParsePackage,
)
from codegen.python_gen.domain.services.python_syntax_translator import (
    PythonSyntaxTranslator,
)
from codegen.python_gen.infrastructure.adapters.black_code_formatter import (
    BlackCodeFormatter,
)
from codegen.shared.infrastructure.adapters.jinja_adapter import JinjaAdapter
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    os_file_port = Singleton(OSFileSystem, config=config)
    template_port_provider = Singleton(JinjaAdapter, config=config)

    blueprint_loader_provider = Singleton(YamlBlueprintStorage, config=config)

    python_syntax_translator_provider = Singleton(
        PythonSyntaxTranslator,
        template_port=template_port_provider,
        file_system_port=os_file_port,
    )

    code_formatter_provider = Singleton(BlackCodeFormatter)

    # Path resolution services
    path_resolver_provider = Singleton(BlueprintPathResolver)

    path_operations_provider = Singleton(
        BlueprintPathOperations,
        resolver=path_resolver_provider,
    )

    load_blueprint_use_case: Factory[LoadBlueprint] = Factory(
        LoadBlueprint,
        blueprint_loader=blueprint_loader_provider,
    )

    generate_package_use_case: Factory[GeneratePackage] = Factory(
        GeneratePackage,
        translator=python_syntax_translator_provider,
        file_system_port=os_file_port,
        code_formatter=code_formatter_provider,
    )

    parse_package_use_case: Factory[ParsePackage] = Factory(
        ParsePackage,
        translator=python_syntax_translator_provider,
    )

    generate_project_use_case: Factory[GenerateProject] = Factory(
        GenerateProject,
        loader=load_blueprint_use_case,
        generator=generate_package_use_case,
    )

    update_blueprint_use_case: Factory[GenerateBlueprint] = Factory(
        GenerateBlueprint,
        parser=parse_package_use_case,
        storage=blueprint_loader_provider,
    )

    # Path-based use cases
    get_value_use_case: Factory[GetValue] = Factory(
        GetValue,
        storage=blueprint_loader_provider,
        operations=path_operations_provider,
    )

    set_value_use_case: Factory[SetValue] = Factory(
        SetValue,
        storage=blueprint_loader_provider,
        operations=path_operations_provider,
    )

    remove_value_use_case: Factory[RemoveValue] = Factory(
        RemoveValue,
        storage=blueprint_loader_provider,
        operations=path_operations_provider,
    )
