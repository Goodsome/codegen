from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Factory, Singleton
from event_hub import EventHub

from codegen.code_metadata.application.commands.generate_code import GenerateCode
from codegen.code_metadata.application.mappers.component_mapper import ComponentDtoMapper
from codegen.code_metadata.application.mappers.parsed_attribute_mapper import ParsedAttributeMapper
from codegen.code_metadata.application.mappers.parsed_component_to_sync_data import ParsedComponentToSyncData
from codegen.code_metadata.application.mappers.parsed_type_to_type_def import ParsedTypeToTypeDef
from codegen.code_metadata.application.queries.get_dev_progress import GetDevProgress
from codegen.code_metadata.application.queries.list_components import ListComponents
from codegen.code_metadata.application.services.dev_progress_service import DevProgressService
from codegen.code_metadata.application.services.project_sync_service import ProjectSyncService
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.infrastructure.gateways.python_code_generator import (
    PythonCodeGenerator,
)
from codegen.code_metadata.infrastructure.gateways.python_code_parser import (
    PythonCodeParser,
)
from codegen.code_metadata.infrastructure.mappers.ast_class_to_component import (
    AstClassToComponent,
)
from codegen.code_metadata.infrastructure.mappers.ast_module_to_component import (
    AstModuleToComponent,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_attribute import AstNodeToParsedAttribute
from codegen.code_metadata.infrastructure.mappers.ast_node_to_parsed_type import AstNodeToParsedType
from codegen.code_metadata.infrastructure.mappers.attribute_to_ast_assign import AttributeToAstAssign
from codegen.code_metadata.infrastructure.mappers.component_to_ast_class import (
    ComponentToAstClass,
)
from codegen.code_metadata.infrastructure.mappers.component_to_ast_module import (
    ComponentToAstModule,
)
from codegen.code_metadata.infrastructure.persistence.repositories.sql_alchemy_component_query_service import (
    SQLAlchemyComponentQueryService,
)
from codegen.code_metadata.infrastructure.persistence.repositories.sql_alchemy_component_repository import (
    SqlAlchemyComponentRepository,
)
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.infrastructure.database import Database
from codegen.shared.infrastructure.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork


class Container(DeclarativeContainer):
    config: Configuration = Configuration()

    database: Dependency[Database] = Dependency(instance_of=Database)
    event_hub: Dependency[EventHub] = Dependency(instance_of=EventHub)
    event_publisher_factory = Dependency()

    file_system_port: Dependency[FileSystemPort] = Dependency(
        instance_of=FileSystemPort
    )

    component_repository_factory: Factory[SqlAlchemyComponentRepository] = Factory(
        SqlAlchemyComponentRepository,
    )

    component_query_service: Factory[SQLAlchemyComponentQueryService] = Factory(
        SQLAlchemyComponentQueryService,
        session_factory=database.provided.session_factory,
    )

    unit_of_work: Factory[SqlAlchemyUnitOfWork[ComponentRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=component_repository_factory.provider,
        event_publisher_factory=event_publisher_factory,
    )

    component_dto_mapper: Singleton[ComponentDtoMapper] = Singleton(
        ComponentDtoMapper,
    )
    
    component_policy_factory: Singleton[ComponentPolicyFactory] = Singleton(
        ComponentPolicyFactory,
    )
    
    ast_node_to_parsed_type: Singleton[AstNodeToParsedType] = Singleton(
        AstNodeToParsedType,
    )
    
    ast_node_to_attribute: Singleton[AstNodeToParsedAttribute] = Singleton(
        AstNodeToParsedAttribute,
        ast_node_to_parsed_type=ast_node_to_parsed_type,
    )

    ast_class_to_component: Singleton[AstClassToComponent] = Singleton(
        AstClassToComponent,
        ast_node_to_attribute=ast_node_to_attribute,
        ast_node_to_parsed_type=ast_node_to_parsed_type,
    )

    ast_module_to_component: Singleton[AstModuleToComponent] = Singleton(
        AstModuleToComponent,
        ast_class_to_component=ast_class_to_component,
    )

    python_code_parser: Factory[PythonCodeParser] = Factory(
        PythonCodeParser,
        mapper=ast_module_to_component,
    )

    list_components: Factory[ListComponents] = Factory(
        ListComponents,
        query_service=component_query_service,
    )
    
    attribute_to_ast_assign: Singleton[AttributeToAstAssign] = Singleton(
        AttributeToAstAssign,
    )

    component_to_ast_class: Singleton[ComponentToAstClass] = Singleton(
        ComponentToAstClass,
        component_policy_factory=component_policy_factory,
        attribute_to_ast_assign=attribute_to_ast_assign,
    )

    component_to_ast_module: Singleton[ComponentToAstModule] = Singleton(
        ComponentToAstModule,
        component_to_ast_class=component_to_ast_class,
        component_policy_factory=component_policy_factory,
    )

    python_code_generator: Factory[PythonCodeGenerator] = Factory(
        PythonCodeGenerator,
        component_to_ast_module=component_to_ast_module,
    )

    generate_code: Factory[GenerateCode] = Factory(
        GenerateCode,
        query_service=component_query_service,
        uow=unit_of_work,
        generator=python_code_generator,
    )

    dev_progress_service: Factory[DevProgressService] = Factory(
        DevProgressService,
        file_system_port=file_system_port,
        generator=python_code_generator,
    )

    get_dev_progress: Factory[GetDevProgress] = Factory(
        GetDevProgress,
        query_service=component_query_service,
        uow=unit_of_work,
        dev_progress_service=dev_progress_service,
    )
    
    parsed_type_to_type_def: Factory[ParsedTypeToTypeDef] = Factory(
        ParsedTypeToTypeDef,
    )
    
    parsed_attribute_mapper: Factory[ParsedAttributeMapper] = Factory(
        ParsedAttributeMapper,
        parsed_type_to_type_def=parsed_type_to_type_def,
    )
    
    parsed_component_to_sync_data: Factory[ParsedComponentToSyncData] = Factory(
        ParsedComponentToSyncData,
        parsed_type_to_type_def=parsed_type_to_type_def,
        parsed_attribute_mapper=parsed_attribute_mapper,
    )

    project_sync_service: Factory[ProjectSyncService] = Factory(
        ProjectSyncService,
        parser=python_code_parser,
        file_system_port=file_system_port,
        component_policy_factory=component_policy_factory,
        uow=unit_of_work,
        parsed_component_to_sync_data=parsed_component_to_sync_data,
    )