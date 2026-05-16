from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Factory, Singleton
from event_hub import EventHub

from codegen.code_metadata.application.commands.create_component import CreateComponent
from codegen.code_metadata.application.commands.reverse_code import ReverseCode
from codegen.code_metadata.application.commands.upsert_component import UpsertComponent
from codegen.code_metadata.application.queries.list_components import ListComponents
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.infrastructure.gateways.python_code_parser import (
    PythonCodeParser,
)
from codegen.code_metadata.infrastructure.mappers.module_to_parsed_component import (
    ModuleToParsedComponent,
)
from codegen.code_metadata.infrastructure.persistence.repositories.sql_alchemy_component_query_service import (
    SQLAlchemyComponentQueryService,
)
from codegen.code_metadata.infrastructure.persistence.repositories.sql_alchemy_component_repository import (
    SqlAlchemyComponentRepository,
)
from codegen.python_gen.application.services.parse_code import ParseCode
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
    parse_code: Dependency[ParseCode] = Dependency(instance_of=ParseCode)

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

    create_component: Factory[CreateComponent] = Factory(
        CreateComponent,
        unit_of_work=unit_of_work,
    )

    upsert_component: Factory[UpsertComponent] = Factory(
        UpsertComponent,
        uow=unit_of_work,
        query_service=component_query_service,
    )

    component_policy_factory: Factory[ComponentPolicyFactory] = Factory(
        ComponentPolicyFactory,
    )

    module_to_parsed_component: Singleton[ModuleToParsedComponent] = Singleton(
        ModuleToParsedComponent,
    )

    python_code_parser: Factory[PythonCodeParser] = Factory(
        PythonCodeParser,
        module_parser=parse_code,
        mapper=module_to_parsed_component,
    )

    list_components: Factory[ListComponents] = Factory(
        ListComponents,
        query_service=component_query_service,
    )

    reverse_code: Factory[ReverseCode] = Factory(
        ReverseCode,
        parser=python_code_parser,
        upsert_component=upsert_component,
        file_system_port=file_system_port,
        component_policy_factory=component_policy_factory,
    )
