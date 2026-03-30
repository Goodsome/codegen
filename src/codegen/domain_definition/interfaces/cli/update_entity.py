"""
UpdateEntity command - Update an existing entity in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_entity import (
    UpdateEntity,
    UpdateEntityCommand,
    UpdateEntityResult,
)


@inject
def _update_entity(
    cmd: UpdateEntityCommand,
    use_case: UpdateEntity = Provide["domain_definition_container.update_entity"],
) -> UpdateEntityResult:
    return use_case.execute(cmd)


def update_entity(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Entity name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing entity in a bounded context.
    """
    cmd = UpdateEntityCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_entity(cmd)
    if result.success:
        typer.echo(f"Successfully updated entity '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update entity '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
