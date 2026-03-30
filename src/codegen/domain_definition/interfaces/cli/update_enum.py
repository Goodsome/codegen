"""
UpdateEnum command - Update an existing enum in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_enum import (
    UpdateEnum,
    UpdateEnumCommand,
    UpdateEnumResult,
)


@inject
def _update_enum(
    cmd: UpdateEnumCommand,
    use_case: UpdateEnum = Provide["domain_definition_container.update_enum"],
) -> UpdateEnumResult:
    return use_case.execute(cmd)


def update_enum(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Enum name")],
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing enum in a bounded context.
    """
    cmd = UpdateEnumCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _update_enum(cmd)
    if result.success:
        typer.echo(f"Successfully updated enum '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update enum '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
