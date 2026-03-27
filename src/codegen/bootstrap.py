from pathlib import Path

from dependency_injector import containers, providers

from codegen.domain_definition.container import Container as DomainDefinitionContainer
from codegen.orchestration.container import Container as OrchestrationContainer
from codegen.python_gen.container import Container as PythonGenContainer
from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    # Shared infrastructure
    os_file_system = providers.Singleton(
        OSFileSystem,
        root=config.project_root,
        encoding=config.encoding,
    )

    # DomainDefinition sub-container
    domain_definition_container = providers.Container(
        DomainDefinitionContainer,
        config=config,
    )

    # PythonGen sub-container
    python_gen_container = providers.Container(
        PythonGenContainer,
        file_system_port=os_file_system,
    )

    # Orchestration sub-container
    orchestration_container = providers.Container(
        OrchestrationContainer,
        load_blueprint=domain_definition_container.load_blueprint,
        generate_package=python_gen_container.generate_package,
        parse_package=python_gen_container.parse_package,
        blueprint_storage=domain_definition_container.yaml_blueprint_storage,
    )


# Global container instance for dependency injection
_container_instance: Container | None = None


def bootstrap() -> Container:
    """Bootstrap the DI container with configuration."""
    global _container_instance
    _container_instance = Container()
    cwd = Path.cwd()
    _container_instance.config.project_root.from_value(cwd)
    _container_instance.config.encoding.from_value("utf-8")
    _container_instance.config.config_path.from_value(cwd / "codegen.yaml")
    return _container_instance
