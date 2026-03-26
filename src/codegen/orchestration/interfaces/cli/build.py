from typing import Annotated
import typer
from codegen.orchestration.container import Container
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectResult,
)

container = Container()


def build(
    overwrite: Annotated[bool, typer.Argument()],
    nodes: Annotated[str, typer.Option(default=None)],
    root_path: Annotated[str, typer.Option(default="''")],
    generate_tests: Annotated[bool, typer.Option(default="False")],
) -> GenerateProjectResult:
    use_case = container.generate_project_use_case()
    cmd = GenerateProjectCommand(
        overwrite=overwrite,
        nodes=nodes,
        root_path=root_path,
        generate_tests=generate_tests,
    )
    return use_case.execute(cmd)
