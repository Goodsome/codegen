import typer
from codegen.orchestration.container import Container
from typing import Annotated, Union
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectResult,
)

container = Container()


def build(
    overwrite: Annotated[bool, typer.Option("False", "--overwrite", "-o")],
    nodes: Annotated[list[str] | None, typer.Option(None, "--nodes", "-n")],
    root_path: Annotated[str, typer.Option("''", "--root-path", "-r")],
    generate_tests: Annotated[bool, typer.Option("False", "--generate-tests", "-g")],
) -> GenerateProjectResult:
    use_case = container.generate_project_use_case()
    cmd = GenerateProjectCommand(
        overwrite=overwrite,
        nodes=nodes,
        root_path=root_path,
        generate_tests=generate_tests,
    )
    return use_case.execute(cmd)
