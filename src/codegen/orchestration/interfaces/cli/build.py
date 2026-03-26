import typer
from codegen.orchestration.container import Container
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
    GenerateProjectResult,
)

container = Container()


def build(cmd: GenerateProjectCommand) -> GenerateProjectResult:
    """Build Python code from blueprint"""
    use_case = container.generate_project_use_case()
    return use_case.execute(cmd)
