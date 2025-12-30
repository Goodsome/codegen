from codegen.python_gen.application.translators.blueprint_trans import (
    BlueprintTranslator,
)
from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Factory

from codegen.domain_definition.application.use_cases.load_blueprint import LoadBlueprint
from codegen.domain_definition.infrastructure.adapters.yaml_blueprint_loader import (
    YamlBlueprintLoader,
)
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
from codegen.shared.infrastructure.adapters.jinja_adapter import JinjaAdapter
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    os_file_port = Singleton(OSFileSystem, config=config)
    template_port_provider = Singleton(JinjaAdapter, config=config)

    blueprint_loader_provider = Singleton(YamlBlueprintLoader, config=config)

    blueprint_translator_provider = Singleton(BlueprintTranslator)

    python_syntax_translator_provider = Singleton(
        PythonSyntaxTranslator,
        template_port=template_port_provider,
        file_system_port=os_file_port,
    )

    load_blueprint_use_case: Factory[LoadBlueprint] = Factory(
        LoadBlueprint,
        blueprint_loader=blueprint_loader_provider,
    )

    generate_package_use_case: Factory[GeneratePackage] = Factory(
        GeneratePackage,
        translator=python_syntax_translator_provider,
        file_system_port=os_file_port,
    )

    parse_package_use_case: Factory[ParsePackage] = Factory(
        ParsePackage,
        translator=python_syntax_translator_provider,
    )

    generate_code_workflow: Factory[GenerateProject] = Factory(
        GenerateProject,
        loader=load_blueprint_use_case,
        generator=generate_package_use_case,
    )
