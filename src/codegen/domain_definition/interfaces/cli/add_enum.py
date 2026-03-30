"""
AddEnum command - Add a new enum to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_enum import (
    AddEnum,
    AddEnumCommand,
    AddEnumResult,
)


@inject
def _add_enum(
    cmd: AddEnumCommand,
    use_case: AddEnum = Provide["domain_definition_container.add_enum"],
) -> AddEnumResult:
    return use_case.execute(cmd)


def add_enum(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Enum name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Enum description")],
) -> None:
    """
    Add a new enum to a bounded context.
    """
    cmd = AddEnumCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_enum(cmd)
    if result.success:
        typer.echo(f"Successfully added enum '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add enum '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
