"""
UpdateValueObject command - Update an existing value object in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_value_object import (
    UpdateValueObject,
    UpdateValueObjectCommand,
    UpdateValueObjectResult,
)


@inject
def _update_value_object(
    cmd: UpdateValueObjectCommand,
    use_case: UpdateValueObject = Provide[
        "domain_definition_container.update_value_object"
    ],
) -> UpdateValueObjectResult:
    return use_case.execute(cmd)


def update_value_object(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Value object name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing value object in a bounded context.
    """
    cmd = UpdateValueObjectCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_value_object(cmd)
    if result.success:
        typer.echo(f"Successfully updated value object '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update value object '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
