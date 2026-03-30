import typer
from codegen.domain_definition.application.use_cases.add_app_port import (
    AddAppPort,
    AddAppPortCommand,
    AddAppPortResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _add_app_port(
    cmd: AddAppPortCommand,
    use_case: AddAppPort = Provide["domain_definition_container.add_app_port"],
) -> AddAppPortResult:
    return use_case.execute(cmd)


def add_app_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App port name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="App port description")],
) -> None:
    """
    Add a new app port to a bounded context.
    """
    cmd = AddAppPortCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_app_port(cmd)
    if result.success:
        typer.echo(f"Successfully added app port '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add app port '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
