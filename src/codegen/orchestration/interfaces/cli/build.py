import typer
from dependency_injector.wiring import Provide, inject
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProject,
    GenerateProjectCommand,
    GenerateProjectResult,
)
from typing import Annotated, Union


@inject
def _do_build(
    cmd: GenerateProjectCommand,
    use_case: GenerateProject = Provide[
        "orchestration_container.generate_project_use_case"
    ],
) -> GenerateProjectResult:
    return use_case.execute(cmd)


def build(
    overwrite: Annotated[bool, typer.Option("False", "--overwrite", "-o")],
    nodes: Annotated[list[str] | None, typer.Option(None, "--nodes", "-n")],
    root_path: Annotated[str, typer.Option("''", "--root-path", "-r")],
    generate_tests: Annotated[bool, typer.Option("False", "--generate-tests", "-g")],
) -> GenerateProjectResult:
    cmd = GenerateProjectCommand(
        overwrite=overwrite,
        nodes=nodes,
        root_path=root_path,
        generate_tests=generate_tests,
    )
    return _do_build(cmd)
