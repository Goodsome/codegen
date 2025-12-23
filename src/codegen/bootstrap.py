from codegen.application.use_cases.load_blueprint import LoadBlueprintHandler
from codegen.orchestration.translators.blueprint_to_package_spec import (
    BlueprintToPackageSpecTranslator,
)
from codegen.orchestration.workflows.generate_project import GenerateCodeWorkflow
from codegen.python_gen.application.use_cases.generate_module import (
    GenerateModuleHandler,
)
from codegen.infrastructure.adapters.yaml_blueprint_loader import YamlBlueprintLoader
from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackageHandler,
)
from codegen.shared.infrastructure.adapters.o_s_file_system import OSFileSystem
from codegen.shared.infrastructure.adapters.jinja_adapter import JinjaAdapter
from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Factory

from codegen.domain.services.scaffold_service import ScaffoldService


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    os_file_port = Singleton(OSFileSystem, config=config)
    template_port_provider = Singleton(JinjaAdapter, config=config)

    scaffold_service_provider = Singleton(ScaffoldService)
    blueprint_loader_provider = Singleton(YamlBlueprintLoader)

    load_blueprint_use_case: Factory[LoadBlueprintHandler] = Factory(
        LoadBlueprintHandler,
        blueprint_loader=blueprint_loader_provider,
    )

    generate_module_use_case: Factory[GenerateModuleHandler] = Factory(
        GenerateModuleHandler,
        template_port=template_port_provider,
        file_system_port=os_file_port,
    )

    generate_code_workflow: Factory[GenerateCodeWorkflow] = Factory(
        GenerateCodeWorkflow,
        loader=load_blueprint_use_case,
        generator=generate_module_use_case,
        translator=BlueprintToPackageSpecTranslator,
    )
