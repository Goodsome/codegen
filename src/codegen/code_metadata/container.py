from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Dependency, Factory
from event_hub import EventHub

from codegen.code_metadata.application.commands.create_component import CreateComponent
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.infrastructure.persistence.repositories.sql_alchemy_component_repository import SqlAlchemyComponentRepository
from codegen.shared.infrastructure.database import Database
from codegen.shared.infrastructure.sql_alchemy_unit_of_work import SqlAlchemyUnitOfWork


class Container(DeclarativeContainer):

    config: Configuration = Configuration()
    
    database: Dependency[Database] = Dependency(instance_of=Database)
    event_hub: Dependency[EventHub] = Dependency(instance_of=EventHub)
    event_publisher_factory = Dependency()
    
    component_repository_factory: Factory[SqlAlchemyComponentRepository] = Factory(
        SqlAlchemyComponentRepository,
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
