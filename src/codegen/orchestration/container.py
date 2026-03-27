from dependency_injector import containers, providers
from dependency_injector.providers import Factory

from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprint,
)
from codegen.orchestration.application.use_cases.generate_project import GenerateProject


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()
    load_blueprint_use_case = providers.Dependency()
    generate_package_use_case = providers.Dependency()

    generate_project_use_case = Factory(
        GenerateProject,
        loader=load_blueprint_use_case,
        generator=generate_package_use_case,
    )
    generate_blueprint_use_case = Factory(
        GenerateBlueprint,
    )
