from codegen.application.use_cases.generate_code import GenerateCodeHandler
from codegen.infrastructure.adapters.yaml_blueprint_loader import YamlBlueprintLoader
from codegen.shared.infrastructure.adapters.o_s_file_system import OSFileSystem
from codegen.shared.infrastructure.adapters.jinja_adapter import JinjaAdapter
from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Factory

from codegen.domain.services.scaffold_service import ScaffoldService


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()
    # If the config comes from a file or dict, you would normally load it:
    # config.from_dict(...) or config.from_yaml(...)

    os_file_port = Singleton(OSFileSystem, config=config)
    template_port_provider = Singleton(JinjaAdapter, config=config)

    scaffold_service_provider = Singleton(ScaffoldService)
    blueprint_loader_provider = Singleton(YamlBlueprintLoader)

    generate_code_use_case: Factory[GenerateCodeHandler] = Factory(
        GenerateCodeHandler,
        template_port=template_port_provider,
        file_system_port=os_file_port,
        blueprint_loader=blueprint_loader_provider,
        scaffold_service=scaffold_service_provider,
    )
