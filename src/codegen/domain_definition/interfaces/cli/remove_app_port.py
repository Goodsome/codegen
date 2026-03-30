import typer
from dependency_injector.wiring import Provide, inject
from codegen.domain_definition.application.use_cases.remove_app_port import (
    RemoveAppPort,
    RemoveAppPortCommand,
    RemoveAppPortResult,
)
from typing import Annotated


@inject
def _remove_app_port(
    cmd: RemoveAppPortCommand,
    use_case: RemoveAppPort = Provide["domain_definition_container.remove_app_port"],
) -> RemoveAppPortResult:
    return use_case.execute(cmd)


def remove_app_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App port name")],
) -> None:
    """
    Remove an app port from a bounded context.
    """
    cmd = RemoveAppPortCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_app_port(cmd)
    if result.success:
        typer.echo(f"Successfully removed app port '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove app port '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
