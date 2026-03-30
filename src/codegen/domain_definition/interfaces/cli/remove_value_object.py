"""
RemoveValueObject command - Remove a value object from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_value_object import (
    RemoveValueObject,
    RemoveValueObjectCommand,
    RemoveValueObjectResult,
)


@inject
def _remove_value_object(
    cmd: RemoveValueObjectCommand,
    use_case: RemoveValueObject = Provide[
        "domain_definition_container.remove_value_object"
    ],
) -> RemoveValueObjectResult:
    return use_case.execute(cmd)


def remove_value_object(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Value object name")],
) -> None:
    """
    Remove a value object from a bounded context.
    """
    cmd = RemoveValueObjectCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_value_object(cmd)
    if result.success:
        typer.echo(f"Successfully removed value object '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove value object '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
