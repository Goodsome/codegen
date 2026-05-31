from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Dependency,
    Factory,
    Singleton,
)
from event_hub import EventHub

from codegen.code_metadata.application.commands.delete_component import DeleteComponent
from codegen.code_metadata.application.commands.generate_code import GenerateCode
from codegen.code_metadata.application.queries.get_dev_progress import GetDevProgress
from codegen.code_metadata.application.queries.list_components import ListComponents
from codegen.code_metadata.application.services.dev_progress_service import (
    DevProgressService,
)
from codegen.code_metadata.application.services.project_sync_service import (
    ProjectSyncService,
)
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.domain.ports.module_repository import ModuleRepository
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.infrastructure.gateways.python_code_generator import (
    PythonCodeGenerator,
)
from codegen.code_metadata.infrastructure.gateways.python_code_parser import (
    PythonCodeParser,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_component_query_service import (
    SqlAlchemyComponentQueryService,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_component_repository import (
    SqlAlchemyComponentRepository,
)
from codegen.code_metadata.infrastructure.repositories.sql_alchemy_module_repository import SqlAlchemyModuleRepository
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

    module_repository_factory: Factory[SqlAlchemyModuleRepository] = Factory(
        SqlAlchemyModuleRepository,
    )

    component_query_service: Factory[SqlAlchemyComponentQueryService] = Factory(
        SqlAlchemyComponentQueryService,
        session_factory=database.provided.session_factory,
    )

    unit_of_work: Factory[SqlAlchemyUnitOfWork[ComponentRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=component_repository_factory.provider,
        event_publisher_factory=event_publisher_factory,
    )

    module_unit_of_work: Factory[SqlAlchemyUnitOfWork[ModuleRepository]] = Factory(
        SqlAlchemyUnitOfWork,
        session_factory=database.provided.session_factory,
        repository_factory=module_repository_factory.provider,
        event_publisher_factory=event_publisher_factory,
    )

    component_policy_factory: Singleton[ComponentPolicyFactory] = Singleton(
        ComponentPolicyFactory,
    )

    python_code_parser: Factory[PythonCodeParser] = Factory(
        PythonCodeParser,
    )

    list_components: Factory[ListComponents] = Factory(
        ListComponents,
        query_service=component_query_service,
    )

    python_code_generator: Factory[PythonCodeGenerator] = Factory(
        PythonCodeGenerator,
        component_policy_factory=component_policy_factory,
    )

    generate_code: Factory[GenerateCode] = Factory(
        GenerateCode,
        query_service=component_query_service,
        uow=unit_of_work,
        generator=python_code_generator,
    )

    delete_component: Factory[DeleteComponent] = Factory(
        DeleteComponent,
        uow=unit_of_work,
    )

    path_parser: Factory[PathParser] = Factory(
        PathParser,
        dir_to_type_registry=component_policy_factory.provided.get_dir_to_type_registry.call(),
    )
    
    dev_progress_service: Factory[DevProgressService] = Factory(
        DevProgressService,
        file_system_port=file_system_port,
        generator=python_code_generator,
        uow=module_unit_of_work,
        path_parser=path_parser,
    )

    get_dev_progress: Factory[GetDevProgress] = Factory(
        GetDevProgress,
        uow=unit_of_work,
        dev_progress_service=dev_progress_service,
    )

    project_sync_service: Factory[ProjectSyncService] = Factory(
        ProjectSyncService,
        parser=python_code_parser,
        file_system_port=file_system_port,
        component_policy_factory=component_policy_factory,
        uow=unit_of_work,
        path_parser=path_parser,
        module_uow=module_unit_of_work,
    )
