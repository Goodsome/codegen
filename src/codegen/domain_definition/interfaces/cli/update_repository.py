"""UpdateRepository command - Update an existing repository in a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_repository import (
    UpdateRepository,
    UpdateRepositoryCommand,
    UpdateRepositoryResult,
)


@inject
def _update_repository(
    cmd: UpdateRepositoryCommand,
    use_case: UpdateRepository = Provide[
        "domain_definition_container.update_repository"
    ],
) -> UpdateRepositoryResult:
    return use_case.execute(cmd)


def update_repository(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Repository name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing repository in a bounded context.
    """
    cmd = UpdateRepositoryCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_repository(cmd)
    if result.success:
        typer.echo(f"Successfully updated repository '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update repository '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
