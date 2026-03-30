"""
AddValueObject command - Add a new value object to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_value_object import (
    AddValueObject,
    AddValueObjectCommand,
    AddValueObjectResult,
)


@inject
def _add_value_object(
    cmd: AddValueObjectCommand,
    use_case: AddValueObject = Provide["domain_definition_container.add_value_object"],
) -> AddValueObjectResult:
    return use_case.execute(cmd)


def add_value_object(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Value object name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Value object description")],
) -> None:
    """
    Add a new value object to a bounded context.
    """
    cmd = AddValueObjectCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_value_object(cmd)
    if result.success:
        typer.echo(f"Successfully added value object '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add value object '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
