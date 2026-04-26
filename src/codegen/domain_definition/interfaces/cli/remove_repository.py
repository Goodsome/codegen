"""RemoveRepository command - Remove a repository from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_repository import (
    RemoveRepository,
    RemoveRepositoryCommand,
    RemoveRepositoryResult,
)


@inject
def _remove_repository(
    cmd: RemoveRepositoryCommand,
    use_case: RemoveRepository = Provide[
        "domain_definition_container.remove_repository"
    ],
) -> RemoveRepositoryResult:
    return use_case.execute(cmd)


def remove_repository(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Repository name")],
) -> None:
    """
    Remove a repository from a bounded context.
    """
    cmd = RemoveRepositoryCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_repository(cmd)
    if result.success:
        typer.echo(f"Successfully removed repository '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove repository '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
