from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton

# Aggregate use cases
from codegen.domain_definition.application.use_cases.add_aggregate import AddAggregate
from codegen.domain_definition.application.use_cases.update_aggregate import UpdateAggregate
from codegen.domain_definition.application.use_cases.get_aggregate import GetAggregate
from codegen.domain_definition.application.use_cases.remove_aggregate import RemoveAggregate

# Entity use cases
from codegen.domain_definition.application.use_cases.add_entity import AddEntity
from codegen.domain_definition.application.use_cases.update_entity import UpdateEntity
from codegen.domain_definition.application.use_cases.get_entity import GetEntity
from codegen.domain_definition.application.use_cases.remove_entity import RemoveEntity

# Value object use cases
from codegen.domain_definition.application.use_cases.add_value_object import AddValueObject
from codegen.domain_definition.application.use_cases.update_value_object import UpdateValueObject
from codegen.domain_definition.application.use_cases.get_value_object import GetValueObject
from codegen.domain_definition.application.use_cases.remove_value_object import RemoveValueObject

# Enum use cases
from codegen.domain_definition.application.use_cases.add_enum import AddEnum
from codegen.domain_definition.application.use_cases.update_enum import UpdateEnum
from codegen.domain_definition.application.use_cases.get_enum import GetEnum
from codegen.domain_definition.application.use_cases.remove_enum import RemoveEnum

# Domain service use cases
from codegen.domain_definition.application.use_cases.add_domain_service import AddDomainService
from codegen.domain_definition.application.use_cases.update_domain_service import UpdateDomainService
from codegen.domain_definition.application.use_cases.get_domain_service import GetDomainService
from codegen.domain_definition.application.use_cases.remove_domain_service import RemoveDomainService

# Domain port use cases
from codegen.domain_definition.application.use_cases.add_domain_port import AddDomainPort
from codegen.domain_definition.application.use_cases.update_domain_port import UpdateDomainPort
from codegen.domain_definition.application.use_cases.get_domain_port import GetDomainPort
from codegen.domain_definition.application.use_cases.remove_domain_port import RemoveDomainPort

# Use case use cases
from codegen.domain_definition.application.use_cases.add_use_case import AddUseCase
from codegen.domain_definition.application.use_cases.update_use_case import UpdateUseCase
from codegen.domain_definition.application.use_cases.get_use_case import GetUseCase
from codegen.domain_definition.application.use_cases.remove_use_case import RemoveUseCase

# App port use cases
from codegen.domain_definition.application.use_cases.add_app_port import AddAppPort
from codegen.domain_definition.application.use_cases.update_app_port import UpdateAppPort
from codegen.domain_definition.application.use_cases.get_app_port import GetAppPort
from codegen.domain_definition.application.use_cases.remove_app_port import RemoveAppPort

# App service use cases
from codegen.domain_definition.application.use_cases.add_app_service import AddAppService
from codegen.domain_definition.application.use_cases.update_app_service import UpdateAppService
from codegen.domain_definition.application.use_cases.get_app_service import GetAppService
from codegen.domain_definition.application.use_cases.remove_app_service import RemoveAppService

# Implementation use cases
from codegen.domain_definition.application.use_cases.add_implementation import AddImplementation
from codegen.domain_definition.application.use_cases.update_implementation import UpdateImplementation
from codegen.domain_definition.application.use_cases.get_implementation import GetImplementation
from codegen.domain_definition.application.use_cases.remove_implementation import RemoveImplementation

# CLI command use cases
from codegen.domain_definition.application.use_cases.add_cli_command import AddCliCommand
from codegen.domain_definition.application.use_cases.update_cli_command import UpdateCliCommand
from codegen.domain_definition.application.use_cases.get_cli_command import GetCliCommand
from codegen.domain_definition.application.use_cases.remove_cli_command import RemoveCliCommand

# MCP tool use cases
from codegen.domain_definition.application.use_cases.add_mcp_tool import AddMcpTool
from codegen.domain_definition.application.use_cases.update_mcp_tool import UpdateMcpTool
from codegen.domain_definition.application.use_cases.get_mcp_tool import GetMcpTool
from codegen.domain_definition.application.use_cases.remove_mcp_tool import RemoveMcpTool

# HTTP endpoint use cases
from codegen.domain_definition.application.use_cases.add_http_endpoint import AddHttpEndpoint
from codegen.domain_definition.application.use_cases.update_http_endpoint import UpdateHttpEndpoint
from codegen.domain_definition.application.use_cases.get_http_endpoint import GetHttpEndpoint
from codegen.domain_definition.application.use_cases.remove_http_endpoint import RemoveHttpEndpoint

# Other use cases
from codegen.domain_definition.application.use_cases.get_value import GetValue
from codegen.domain_definition.application.use_cases.init_project import InitProject
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

    init_project = Factory(InitProject, storage=yaml_blueprint_storage)

    # =========================================================================
    # Aggregate use cases
    # =========================================================================
    add_aggregate = Factory(AddAggregate, storage=yaml_blueprint_storage)
    update_aggregate = Factory(UpdateAggregate, storage=yaml_blueprint_storage)
    get_aggregate = Factory(GetAggregate, storage=yaml_blueprint_storage)
    remove_aggregate = Factory(RemoveAggregate, storage=yaml_blueprint_storage)

    # =========================================================================
    # Entity use cases
    # =========================================================================
    add_entity = Factory(AddEntity, storage=yaml_blueprint_storage)
    update_entity = Factory(UpdateEntity, storage=yaml_blueprint_storage)
    get_entity = Factory(GetEntity, storage=yaml_blueprint_storage)
    remove_entity = Factory(RemoveEntity, storage=yaml_blueprint_storage)

    # =========================================================================
    # Value object use cases
    # =========================================================================
    add_value_object = Factory(AddValueObject, storage=yaml_blueprint_storage)
    update_value_object = Factory(UpdateValueObject, storage=yaml_blueprint_storage)
    get_value_object = Factory(GetValueObject, storage=yaml_blueprint_storage)
    remove_value_object = Factory(RemoveValueObject, storage=yaml_blueprint_storage)

    # =========================================================================
    # Enum use cases
    # =========================================================================
    add_enum = Factory(AddEnum, storage=yaml_blueprint_storage)
    update_enum = Factory(UpdateEnum, storage=yaml_blueprint_storage)
    get_enum = Factory(GetEnum, storage=yaml_blueprint_storage)
    remove_enum = Factory(RemoveEnum, storage=yaml_blueprint_storage)

    # =========================================================================
    # Domain service use cases
    # =========================================================================
    add_domain_service = Factory(AddDomainService, storage=yaml_blueprint_storage)
    update_domain_service = Factory(UpdateDomainService, storage=yaml_blueprint_storage)
    get_domain_service = Factory(GetDomainService, storage=yaml_blueprint_storage)
    remove_domain_service = Factory(RemoveDomainService, storage=yaml_blueprint_storage)

    # =========================================================================
    # Domain port use cases
    # =========================================================================
    add_domain_port = Factory(AddDomainPort, storage=yaml_blueprint_storage)
    update_domain_port = Factory(UpdateDomainPort, storage=yaml_blueprint_storage)
    get_domain_port = Factory(GetDomainPort, storage=yaml_blueprint_storage)
    remove_domain_port = Factory(RemoveDomainPort, storage=yaml_blueprint_storage)

    # =========================================================================
    # Use case use cases
    # =========================================================================
    add_use_case = Factory(AddUseCase, storage=yaml_blueprint_storage)
    update_use_case = Factory(UpdateUseCase, storage=yaml_blueprint_storage)
    get_use_case = Factory(GetUseCase, storage=yaml_blueprint_storage)
    remove_use_case = Factory(RemoveUseCase, storage=yaml_blueprint_storage)

    # =========================================================================
    # App port use cases
    # =========================================================================
    add_app_port = Factory(AddAppPort, storage=yaml_blueprint_storage)
    update_app_port = Factory(UpdateAppPort, storage=yaml_blueprint_storage)
    get_app_port = Factory(GetAppPort, storage=yaml_blueprint_storage)
    remove_app_port = Factory(RemoveAppPort, storage=yaml_blueprint_storage)

    # =========================================================================
    # App service use cases
    # =========================================================================
    add_app_service = Factory(AddAppService, storage=yaml_blueprint_storage)
    update_app_service = Factory(UpdateAppService, storage=yaml_blueprint_storage)
    get_app_service = Factory(GetAppService, storage=yaml_blueprint_storage)
    remove_app_service = Factory(RemoveAppService, storage=yaml_blueprint_storage)

    # =========================================================================
    # Implementation use cases
    # =========================================================================
    add_implementation = Factory(AddImplementation, storage=yaml_blueprint_storage)
    update_implementation = Factory(UpdateImplementation, storage=yaml_blueprint_storage)
    get_implementation = Factory(GetImplementation, storage=yaml_blueprint_storage)
    remove_implementation = Factory(RemoveImplementation, storage=yaml_blueprint_storage)

    # =========================================================================
    # CLI command use cases
    # =========================================================================
    add_cli_command = Factory(AddCliCommand, storage=yaml_blueprint_storage)
    update_cli_command = Factory(UpdateCliCommand, storage=yaml_blueprint_storage)
    get_cli_command = Factory(GetCliCommand, storage=yaml_blueprint_storage)
    remove_cli_command = Factory(RemoveCliCommand, storage=yaml_blueprint_storage)

    # =========================================================================
    # MCP tool use cases
    # =========================================================================
    add_mcp_tool = Factory(AddMcpTool, storage=yaml_blueprint_storage)
    update_mcp_tool = Factory(UpdateMcpTool, storage=yaml_blueprint_storage)
    get_mcp_tool = Factory(GetMcpTool, storage=yaml_blueprint_storage)
    remove_mcp_tool = Factory(RemoveMcpTool, storage=yaml_blueprint_storage)

    # =========================================================================
    # HTTP endpoint use cases
    # =========================================================================
    add_http_endpoint = Factory(AddHttpEndpoint, storage=yaml_blueprint_storage)
    update_http_endpoint = Factory(UpdateHttpEndpoint, storage=yaml_blueprint_storage)
    get_http_endpoint = Factory(GetHttpEndpoint, storage=yaml_blueprint_storage)
    remove_http_endpoint = Factory(RemoveHttpEndpoint, storage=yaml_blueprint_storage)
