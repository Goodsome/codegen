"""
RemoveEntity command - Remove an entity from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_entity import (
    RemoveEntity,
    RemoveEntityCommand,
    RemoveEntityResult,
)


@inject
def _remove_entity(
    cmd: RemoveEntityCommand,
    use_case: RemoveEntity = Provide["domain_definition_container.remove_entity"],
) -> RemoveEntityResult:
    return use_case.execute(cmd)


def remove_entity(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Entity name")],
) -> None:
    """
    Remove an entity from a bounded context.
    """
    cmd = RemoveEntityCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_entity(cmd)
    if result.success:
        typer.echo(f"Successfully removed entity '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove entity '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
