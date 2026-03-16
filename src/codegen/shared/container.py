from codegen.shared.infrastructure.adapters.os_file_system import OSFileSystem
from dependency_injector.providers import Factory
from dependency_injector.containers import DeclarativeContainer


class Container(DeclarativeContainer):
    os_file_system = Factory(OSFileSystem)
