"""
AddEntity command - Add a new entity to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_entity import (
    AddEntity,
    AddEntityCommand,
    AddEntityResult,
)


@inject
def _add_entity(
    cmd: AddEntityCommand,
    use_case: AddEntity = Provide["domain_definition_container.add_entity"],
) -> AddEntityResult:
    return use_case.execute(cmd)


def add_entity(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Entity name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Entity description")],
) -> None:
    """
    Add a new entity to a bounded context.
    """
    cmd = AddEntityCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_entity(cmd)
    if result.success:
        typer.echo(f"Successfully added entity '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add entity '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
