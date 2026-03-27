from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton

from codegen.domain_definition.application.use_cases.get_value import GetValue
from codegen.domain_definition.application.use_cases.load_blueprint import LoadBlueprint
from codegen.domain_definition.application.use_cases.remove_context import RemoveContext
from codegen.domain_definition.application.use_cases.remove_value import RemoveValue
from codegen.domain_definition.application.use_cases.set_value import SetValue
from codegen.domain_definition.application.use_cases.upsert_context import UpsertContext
from codegen.domain_definition.domain.services.blueprint_path_operations import (
    BlueprintPathOperations,
)
from codegen.domain_definition.domain.services.blueprint_path_resolver import (
    BlueprintPathResolver,
)
from codegen.domain_definition.infrastructure.adapters.yaml_blueprint_storage import (
    YamlBlueprintStorage,
)


class Container(DeclarativeContainer):
    config = Configuration()

    yaml_blueprint_storage = Singleton(
        YamlBlueprintStorage,
        config_path=config.config_path,
    )

    path_resolver = Singleton(BlueprintPathResolver)

    path_operations = Singleton(
        BlueprintPathOperations,
        resolver=path_resolver,
    )

    load_blueprint = Factory(LoadBlueprint, blueprint_loader=yaml_blueprint_storage)

    get_value = Factory(
        GetValue,
        storage=yaml_blueprint_storage,
        operations=path_operations,
    )

    set_value = Factory(SetValue, storage=yaml_blueprint_storage, operations=path_operations)

    remove_value = Factory(RemoveValue, storage=yaml_blueprint_storage, operations=path_operations)

    remove_context = Factory(RemoveContext, storage=yaml_blueprint_storage)

    upsert_context = Factory(UpsertContext, storage=yaml_blueprint_storage)
