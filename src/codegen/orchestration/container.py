from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprint,
)
from dependency_injector.providers import Factory
from dependency_injector.containers import DeclarativeContainer
from codegen.orchestration.application.use_cases.generate_project import GenerateProject


class Container(DeclarativeContainer):
    generate_project = Factory(GenerateProject)
    generate_blueprint = Factory(GenerateBlueprint)
