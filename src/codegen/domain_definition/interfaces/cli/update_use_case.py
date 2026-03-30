import typer
from dependency_injector.wiring import Provide, inject
from typing import Annotated, Union
from codegen.domain_definition.application.use_cases.update_use_case import (
    UpdateUseCase,
    UpdateUseCaseCommand,
    UpdateUseCaseResult,
)


@inject
def _update_use_case(
    cmd: UpdateUseCaseCommand,
    use_case: UpdateUseCase = Provide["domain_definition_container.update_use_case"],
) -> UpdateUseCaseResult:
    return use_case.execute(cmd)


def update_use_case(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Use case name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing use case in a bounded context.
    """
    cmd = UpdateUseCaseCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_use_case(cmd)
    if result.success:
        typer.echo(f"Successfully updated use case '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update use case '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
