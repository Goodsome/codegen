from dependency_injector import containers
from dependency_injector.providers import Singleton, Container, Configuration

from codegen.domain_definition.container import Container as DomainDefinitionContainer
from codegen.orchestration.container import Container as OrchestrationContainer
from codegen.python_gen.container import Container as PythonGenContainer
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem
from codegen.shared.container import Container as SharedContainer
from codegen.code_metadata.container import Container as CodeMetadataContainer
from codegen.code_dom.container import Container as CodeDomContainer


class AppContainer(containers.DeclarativeContainer):
    config: Configuration = Configuration()

    # Shared infrastructure
    os_file_system: Singleton[OSFileSystem] = Singleton(
        OSFileSystem,
        root=config.project_root,
        encoding=config.encoding,
    )

    shared_container: Container[SharedContainer] = Container(
        SharedContainer,
        config=config.shared,
    )

    domain_definition_container: Container[DomainDefinitionContainer] = Container(
        DomainDefinitionContainer,
        config=config,
    )

    # PythonGen sub-container
    python_gen_container: Container[PythonGenContainer] = Container(
        PythonGenContainer,
        file_system_port=os_file_system,
    )

    code_dom_container: Container[CodeDomContainer] = Container(
        CodeDomContainer,
        file_system_port=os_file_system,
    )

    code_metadata_container: Container[CodeMetadataContainer] = Container(
        CodeMetadataContainer,
        database=shared_container.database,
        event_publisher_factory=shared_container.event_publisher_factory,
        event_hub=shared_container.event_hub,
        file_system_port=os_file_system,
        project_root=config.project_root,
        get_project_documents=code_dom_container.get_project_documents,
    )

    # DomainDefinition sub-container
    # Orchestration sub-container
    orchestration_container: Container[OrchestrationContainer] = Container(
        OrchestrationContainer,
        load_blueprint=domain_definition_container.load_blueprint,
        generate_package=python_gen_container.generate_package,
        parse_package=python_gen_container.parse_package,
        blueprint_storage=domain_definition_container.yaml_blueprint_storage,
    )
