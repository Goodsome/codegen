"""AddRepository command - Add a new repository to a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_repository import (
    AddRepository,
    AddRepositoryCommand,
    AddRepositoryResult,
)


@inject
def _add_repository(
    cmd: AddRepositoryCommand,
    use_case: AddRepository = Provide[
        "domain_definition_container.add_repository"
    ],
) -> AddRepositoryResult:
    return use_case.execute(cmd)


def add_repository(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Repository name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Repository description")],
) -> None:
    """
    Add a new repository to a bounded context.
    """
    cmd = AddRepositoryCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_repository(cmd)
    if result.success:
        typer.echo(f"Successfully added repository '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add repository '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
