"""
RemoveEnum command - Remove an enum from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_enum import (
    RemoveEnum,
    RemoveEnumCommand,
    RemoveEnumResult,
)


@inject
def _remove_enum(
    cmd: RemoveEnumCommand,
    use_case: RemoveEnum = Provide["domain_definition_container.remove_enum"],
) -> RemoveEnumResult:
    return use_case.execute(cmd)


def remove_enum(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Enum name")],
) -> None:
    """
    Remove an enum from a bounded context.
    """
    cmd = RemoveEnumCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_enum(cmd)
    if result.success:
        typer.echo(f"Successfully removed enum '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove enum '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
