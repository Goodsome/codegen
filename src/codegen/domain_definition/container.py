from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton

from codegen.domain_definition.application.use_cases.init_project import InitProject
from codegen.domain_definition.application.use_cases.load_blueprint import LoadBlueprint

from codegen.domain_definition.infrastructure.adapters.yaml_blueprint_storage import (
    YamlBlueprintStorage,
)


class Container(DeclarativeContainer):
    config = Configuration()

    yaml_blueprint_storage = Singleton(
        YamlBlueprintStorage,
        config_path=config.config_path,
    )

    load_blueprint = Factory(LoadBlueprint, blueprint_loader=yaml_blueprint_storage)

    init_project = Factory(InitProject, storage=yaml_blueprint_storage)
