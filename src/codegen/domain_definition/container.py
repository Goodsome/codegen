from codegen.domain_definition.application.use_cases.remove_value import RemoveValue
from codegen.domain_definition.application.use_cases.set_value import SetValue
from codegen.domain_definition.infrastructure.adapters.yaml_blueprint_storage import (
    YamlBlueprintStorage,
)
from dependency_injector.providers import Factory
from codegen.domain_definition.application.use_cases.get_value import GetValue
from dependency_injector.containers import DeclarativeContainer
from codegen.domain_definition.application.use_cases.load_blueprint import LoadBlueprint


class Container(DeclarativeContainer):
    yaml_blueprint_storage = Factory(YamlBlueprintStorage)
    set_value = Factory(SetValue, storage=yaml_blueprint_storage)
    remove_value = Factory(RemoveValue, storage=yaml_blueprint_storage)
    get_value = Factory(GetValue, storage=yaml_blueprint_storage)
    load_blueprint = Factory(LoadBlueprint, blueprint_loader=yaml_blueprint_storage)
