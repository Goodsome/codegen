import typer
from codegen.domain_definition.application.use_cases.update_app_service import (
    UpdateAppService,
    UpdateAppServiceCommand,
    UpdateAppServiceResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _update_app_service(
    cmd: UpdateAppServiceCommand,
    use_case: UpdateAppService = Provide[
        "domain_definition_container.update_app_service"
    ],
) -> UpdateAppServiceResult:
    return use_case.execute(cmd)


def update_app_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App service name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing app service in a bounded context.
    """
    cmd = UpdateAppServiceCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_app_service(cmd)
    if result.success:
        typer.echo(f"Successfully updated app service '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update app service '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
