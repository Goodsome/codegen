import typer
from codegen.domain_definition.application.use_cases.update_app_port import (
    UpdateAppPort,
    UpdateAppPortCommand,
    UpdateAppPortResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _update_app_port(
    cmd: UpdateAppPortCommand,
    use_case: UpdateAppPort = Provide["domain_definition_container.update_app_port"],
) -> UpdateAppPortResult:
    return use_case.execute(cmd)


def update_app_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App port name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing app port in a bounded context.
    """
    cmd = UpdateAppPortCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_app_port(cmd)
    if result.success:
        typer.echo(f"Successfully updated app port '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update app port '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
