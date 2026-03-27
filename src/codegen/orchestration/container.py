from codegen.orchestration.application.use_cases.generate_blueprint import GenerateBlueprint
from codegen.orchestration.application.use_cases.generate_project import GenerateProject
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Dependency, Factory


class Container(DeclarativeContainer):
    load_blueprint = Dependency()
    generate_package = Dependency()
    parse_package = Dependency()
    blueprint_storage = Dependency()

    generate_project = Factory(
        GenerateProject,
        loader=load_blueprint,
        generator=generate_package,
    )

    generate_blueprint = Factory(
        GenerateBlueprint,
        parser=parse_package,
        storage=blueprint_storage,
    )
