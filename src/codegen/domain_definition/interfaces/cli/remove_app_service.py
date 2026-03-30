import typer
from codegen.domain_definition.application.use_cases.remove_app_service import (
    RemoveAppService,
    RemoveAppServiceCommand,
    RemoveAppServiceResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _remove_app_service(
    cmd: RemoveAppServiceCommand,
    use_case: RemoveAppService = Provide[
        "domain_definition_container.remove_app_service"
    ],
) -> RemoveAppServiceResult:
    return use_case.execute(cmd)


def remove_app_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App service name")],
) -> None:
    """
    Remove an app service from a bounded context.
    """
    cmd = RemoveAppServiceCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_app_service(cmd)
    if result.success:
        typer.echo(f"Successfully removed app service '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove app service '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
