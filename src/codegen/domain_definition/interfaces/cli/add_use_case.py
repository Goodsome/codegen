import typer
from codegen.domain_definition.application.use_cases.add_use_case import (
    AddUseCase,
    AddUseCaseCommand,
    AddUseCaseResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _add_use_case(
    cmd: AddUseCaseCommand,
    use_case: AddUseCase = Provide["domain_definition_container.add_use_case"],
) -> AddUseCaseResult:
    return use_case.execute(cmd)


def add_use_case(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Use case name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Use case description")],
) -> None:
    """
    Add a new use case to a bounded context.
    """
    cmd = AddUseCaseCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_use_case(cmd)
    if result.success:
        typer.echo(f"Successfully added use case '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add use case '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
