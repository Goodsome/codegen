import typer
from codegen.domain_definition.application.use_cases.remove_use_case import (
    RemoveUseCase,
    RemoveUseCaseCommand,
    RemoveUseCaseResult,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


@inject
def _remove_use_case(
    cmd: RemoveUseCaseCommand,
    use_case: RemoveUseCase = Provide["domain_definition_container.remove_use_case"],
) -> RemoveUseCaseResult:
    return use_case.execute(cmd)


def remove_use_case(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Use case name")],
) -> None:
    """
    Remove a use case from a bounded context.
    """
    cmd = RemoveUseCaseCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_use_case(cmd)
    if result.success:
        typer.echo(f"Successfully removed use case '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove use case '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
