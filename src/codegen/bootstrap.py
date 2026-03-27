from pathlib import Path

from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Factory

from codegen.domain_definition.application.use_cases.load_blueprint import LoadBlueprint
from codegen.domain_definition.application.use_cases.get_value import (
    GetValue,
)
from codegen.domain_definition.application.use_cases.set_value import SetValue
from codegen.domain_definition.application.use_cases.remove_value import RemoveValue
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
from codegen.python_gen.infrastructure.adapters.ast_translator import AstTranslator
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem
from codegen.domain_definition.container import Container as DomainDefinitionContainer
from codegen.orchestration.container import Container as OrchestrationContainer
from codegen.python_gen.container import Container as PythonGenContainer


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    os_file_port = Singleton(
        OSFileSystem,
        root=config.project_root,
        encoding=config.encoding,
    )
    ast_translator_provider = Singleton(AstTranslator)

    blueprint_loader_provider = Singleton(
        YamlBlueprintStorage,
        config_path=config.config_path
    )

    python_syntax_translator_provider = Singleton(
        PythonSyntaxTranslator,
        source_code_port=ast_translator_provider,
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

    # Orchestration sub-container
    orchestration_container = providers.Container(
        OrchestrationContainer,
        config=config,
        load_blueprint_use_case=load_blueprint_use_case,
        generate_package_use_case=generate_package_use_case,
        generate_blueprint_use_case=update_blueprint_use_case,
    )

    # DomainDefinition sub-container
    domain_definition_container = providers.Container(
        DomainDefinitionContainer,
        config=config,
    )

    # PythonGen sub-container
    python_gen_container = providers.Container(
        PythonGenContainer,
        file_system_port=os_file_port,
    )


# Global container instance for dependency injection
_container_instance: Container | None = None


def bootstrap() -> Container:
    """Bootstrap the DI container with configuration."""
    global _container_instance
    _container_instance = Container()
    cwd = Path.cwd()
    _container_instance.config.project_root.from_value(cwd)
    _container_instance.config.encoding.from_value("utf-8")
    _container_instance.config.config_path.from_value(cwd / "codegen.yaml")
    return _container_instance


def get_container() -> Container:
    """Get or create the global container instance."""
    global _container_instance
    if _container_instance is None:
        return bootstrap()
    return _container_instance
