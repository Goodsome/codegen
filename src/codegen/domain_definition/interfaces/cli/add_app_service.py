import typer
from codegen.domain_definition.application.use_cases.add_app_service import (
    AddAppService,
    AddAppServiceCommand,
    AddAppServiceResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _add_app_service(
    cmd: AddAppServiceCommand,
    use_case: AddAppService = Provide["domain_definition_container.add_app_service"],
) -> AddAppServiceResult:
    return use_case.execute(cmd)


def add_app_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="App service name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="App service description")],
) -> None:
    """
    Add a new app service to a bounded context.
    """
    cmd = AddAppServiceCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_app_service(cmd)
    if result.success:
        typer.echo(f"Successfully added app service '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add app service '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
